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


def extract_journal_from_citation(citation):
    if not citation or not isinstance(citation, str):
        return ''
    # citation example: "Computer Methods in Applied Mechanics and Engineering 372, 113376, 2020"
    parts = citation.split(',')
    if parts:
        first = parts[0].strip()
        # 从末尾去掉年份数字
        first_parts = first.rsplit(' ', 1)
        if first_parts and len(first_parts) > 1 and first_parts[-1].isdigit():
            return first_parts[0].strip()
        return first
    return ''


def fetch_publications(scholar_id, max_pubs=100):
    author = scholarly.search_author_id(scholar_id)
    author = scholarly.fill(author, sections=["publications"])
    pubs = []
    for p in author.get('publications', [])[:max_pubs]:
        try:
            p = scholarly.fill(p)  # 获取详细bib信息
        except Exception:
            pass
        bib = p.get('bib', {}) if isinstance(p, dict) else {}
        title = bib.get('title', '')
        authors = bib.get('author', author.get('name', ''))
        journal = bib.get('journal', '') or bib.get('venue', '') or extract_journal_from_citation(bib.get('citation', ''))
        year = bib.get('pub_year', '') or bib.get('year', '')
        if isinstance(year, int):
            year = str(year)
        elif isinstance(year, str) and not year.isdigit():
            year = ''.join(filter(str.isdigit, year))
        num_citations = p.get('num_citations', 0)
        url = bib.get('url', '') or p.get('pub_url', '') or p.get('citedby_url', '')

        pub = {
            'title': title,
            'authors': authors,
            'journal': journal,
            'year': year,
            'citations': num_citations,
            'url': url,
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
