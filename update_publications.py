#!/usr/bin/env python3
"""从 Google Scholar 同步发表信息并输出 publications.json，用于个人主页自动更新。"""

import argparse
import json
import sys
import time

try:
    from scholarly import scholarly
except ImportError:
    print("请先安装依赖: pip install scholarly", file=sys.stderr)
    sys.exit(1)


def fetch_publications(scholar_id, max_pubs=50):
    author = scholarly.search_author_id(scholar_id)
    author = scholarly.fill(author, sections=["publications"])
    pubs = []
    for p in author.get('publications', [])[:max_pubs]:
        pub = {
            'title': p.get('bib', {}).get('title', ''),
            'authors': p.get('bib', {}).get('author', ''),
            'journal': p.get('bib', {}).get('venue', '') or p.get('bib', {}).get('journal', ''),
            'year': p.get('bib', {}).get('year', ''),
            'url': p.get('bib', {}).get('url', '') or p.get('pub_url', ''),
        }
        pubs.append(pub)
    return pubs


def main():
    parser = argparse.ArgumentParser(description='同步 Google Scholar 发表信息到 publications.json')
    parser.add_argument('--id', required=True, help='Google Scholar user id，例如 Pb-GVZQAAAAJ')
    parser.add_argument('--output', default='publications.json')
    parser.add_argument('--max', type=int, default=100)
    args = parser.parse_args()

    print(f"开始同步 Scholar ID={args.id} ...")
    try:
        pubs = fetch_publications(args.id, args.max)
    except Exception as e:
        print('获取 Scholar 文章失败:', e, file=sys.stderr)
        sys.exit(1)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(pubs, f, ensure_ascii=False, indent=2)

    print(f"写入 {args.output}, 文章数量：{len(pubs)}")


if __name__ == '__main__':
    main()
