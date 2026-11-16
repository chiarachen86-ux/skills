#!/usr/bin/env python3
"""Read-only, dependency-free PNG batch checks; never approves visual content."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import time
import zlib


def png_info(data):
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Not a PNG')
    pos, chunks, idat, profile = 8, [], [], False
    width = height = depth = color = interlace = None
    srgb = False
    while pos < len(data):
        if pos + 12 > len(data):
            raise ValueError('Truncated chunk')
        length = struct.unpack('>I', data[pos:pos+4])[0]
        kind = data[pos+4:pos+8]
        end = pos + 12 + length
        if end > len(data):
            raise ValueError('Truncated payload')
        payload = data[pos+8:end-4]
        if zlib.crc32(kind+payload) & 0xffffffff != struct.unpack('>I', data[end-4:end])[0]:
            raise ValueError('PNG CRC mismatch')
        if not chunks and kind != b'IHDR':
            raise ValueError('Missing first IHDR')
        chunks.append(kind)
        if kind == b'IHDR':
            if chunks.count(kind) != 1 or length != 13:
                raise ValueError('Invalid IHDR')
            width, height, depth, color, comp, filt, interlace = struct.unpack('>IIBBBBB', payload)
            valid = {0:(1,2,4,8,16), 2:(8,16), 3:(1,2,4,8), 4:(8,16), 6:(8,16)}
            if not width or not height or width*height > 100_000_000 or depth not in valid.get(color, ()) or comp or filt or interlace not in (0,1):
                raise ValueError('Unsupported or invalid PNG header')
        elif kind == b'IDAT':
            idat.append(payload)
        elif kind == b'sRGB':
            if len(payload) != 1 or payload[0] > 3:
                raise ValueError('Invalid sRGB chunk')
            srgb = True
        elif kind == b'iCCP':
            name, rest = payload.split(b'\0', 1)
            if not name or not rest or rest[0] != 0:
                raise ValueError('Invalid ICC encoding')
            icc = zlib.decompress(rest[1:])
            if len(icc) < 128 or icc[36:40] != b'acsp' or struct.unpack('>I', icc[:4])[0] != len(icc):
                raise ValueError('Invalid ICC profile')
            profile = True
        elif kind == b'IEND':
            if length or end != len(data):
                raise ValueError('Invalid IEND or trailing data')
            break
        elif kind[0] & 32 == 0 and kind != b'PLTE':
            raise ValueError('Unknown critical chunk')
        pos = end
    if not chunks or chunks[-1] != b'IEND' or not idat or (color == 3 and b'PLTE' not in chunks):
        raise ValueError('Incomplete PNG')
    channels = {0:1,2:3,3:1,4:2,6:4}[color]
    passes = [(0,0,1,1)] if not interlace else [(0,0,8,8),(4,0,8,8),(0,4,4,8),(2,0,4,4),(0,2,2,4),(1,0,2,2),(0,1,1,2)]
    rows = []
    for x,y,dx,dy in passes:
        w, h = max(0,(width-x+dx-1)//dx), max(0,(height-y+dy-1)//dy)
        if w and h:
            rows.extend([1+(w*channels*depth+7)//8]*h)
    expected = sum(rows)
    decoder = zlib.decompressobj()
    raw = decoder.decompress(b''.join(idat), expected+1)
    if len(raw) != expected or not decoder.eof or decoder.unused_data:
        raise ValueError('Invalid pixel stream length')
    offset = 0
    for row in rows:
        if raw[offset] > 4:
            raise ValueError('Invalid scanline filter')
        offset += row
    return dict(width=width,height=height,square=width==height,icc_present=profile,srgb_chunk=srgb,
                color_status='sRGB declared' if srgb else 'ICC present; color space needs verification' if profile else 'missing color tag')


def check(manifest, min_pixels=2000):
    seen, results = set(), []
    for item in manifest:
        path = Path(item['path']).resolve()
        result = dict(path=str(path),visual_review='pending',technical_errors=[])
        if str(path) in seen:
            result['technical_errors'].append('Duplicate output path')
        seen.add(str(path))
        try:
            data = path.read_bytes()
            result.update(png_info(data),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
            if not result['square']:
                result['technical_errors'].append('Non-square')
            if min(result['width'],result['height']) < min_pixels:
                result['technical_errors'].append('Below requested pixel standard')
            if not result['icc_present'] and not result['srgb_chunk']:
                result['technical_errors'].append('Missing color tag')
            if item.get('sha256') and item['sha256'] != result['sha256']:
                result['technical_errors'].append('Manifest hash differs')
        except (OSError, ValueError, zlib.error, struct.error) as exc:
            result['technical_errors'].append(str(exc))
        results.append(result)
    return dict(expected=len(manifest),checked=len(results),technical_ok=sum(not r['technical_errors'] for r in results),
                visual_review='pending; not inferred from technical checks',files=results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path,help='JSON array of {path, optional sha256}; explicit output list only')
    parser.add_argument('--report',required=True,type=Path)
    parser.add_argument('--min-pixels',type=int,default=2000)
    args = parser.parse_args()
    if args.min_pixels < 1:
        parser.error('--min-pixels must be positive; any standard exception must be authorized')
    if args.report.resolve() == args.manifest.resolve():
        parser.error('Report must not overwrite manifest')
    items = json.loads(args.manifest.read_text())
    if not isinstance(items,list) or not items:
        parser.error('Manifest must be a nonempty list')
    if any(Path(v['path']).resolve() == args.report.resolve() for v in items):
        parser.error('Report must not overwrite an input')
    start = time.monotonic()
    report = check(items,args.min_pixels)
    report['elapsed_seconds'] = round(time.monotonic()-start,3)
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='files'},ensure_ascii=False))
    raise SystemExit(0 if report['technical_ok']==report['expected'] else 1)
