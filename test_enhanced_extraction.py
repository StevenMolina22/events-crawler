#!/usr/bin/env python3
"""
Integration test script for enhanced JSON extraction functionality.

This script tests the enhanced extraction capabilities on real HTML files
and compares the results with the original incomplete extraction.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from show_up.extractors.json_extractor import JsonExtractor
from show_up.utils.validation import validate_event_data, get_data_completeness_score


def test_extraction_on_html_files():
    """Test extraction on all HTML files in the output directory."""

    html_dir = Path("output/html")
    if not html_dir.exists():
        print(f"❌ HTML directory {html_dir} does not exist")
        return

    html_files = list(html_dir.glob("*.html"))
    if not html_files:
        print(f"❌ No HTML files found in {html_dir}")
        return

    print(f"🚀 Testing enhanced extraction on {len(html_files)} HTML files...")
    print()

    extractor = JsonExtractor()
    results = []

    for html_file in html_files:
        print(f"📄 Processing: {html_file.name}")

        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Extract event data
            extracted_data = extractor.extract(html_content, url=f"https://lu.ma/{html_file.stem}")

            if extracted_data:
                # Validate the data
                try:
                    validated_data = validate_event_data(extracted_data)
                    completeness_score = get_data_completeness_score(validated_data)

                    result = {
                        'file': html_file.name,
                        'extraction_success': True,
                        'extraction_method': extracted_data.get('extraction_method', 'unknown'),
                        'extraction_pattern': extracted_data.get('extraction_pattern', 'unknown'),
                        'title': validated_data.get('title', 'Unknown'),
                        'date': validated_data.get('date', 'No date'),
                        'location': validated_data.get('location', 'No location'),
                        'completeness_score': completeness_score,
                        'field_count': len([v for v in validated_data.values() if v not in [None, '', {}]]),
                        'data': validated_data
                    }

                    print(f"  ✅ Success: {result['title']}")
                    print(f"     📅 Date: {result['date']}")
                    print(f"     📍 Location: {result['location']}")
                    print(f"     🔍 Method: {result['extraction_method']} (pattern {result['extraction_pattern']})")
                    print(f"     📊 Completeness: {completeness_score:.2f} ({result['field_count']} fields)")

                except Exception as e:
                    result = {
                        'file': html_file.name,
                        'extraction_success': True,
                        'validation_error': str(e),
                        'raw_data': extracted_data
                    }
                    print(f"  ⚠️  Extraction succeeded but validation failed: {e}")
            else:
                result = {
                    'file': html_file.name,
                    'extraction_success': False,
                    'error': 'No data extracted'
                }
                print(f"  ❌ Failed to extract data")

            results.append(result)

        except Exception as e:
            result = {
                'file': html_file.name,
                'extraction_success': False,
                'error': str(e)
            }
            results.append(result)
            print(f"  ❌ Error: {e}")

        print()

    # Generate summary report
    generate_summary_report(results)

    # Save detailed results
    save_detailed_results(results)

    # Test completed successfully
    assert len(results) > 0, "No results generated"
    assert all(r.get('extraction_success') for r in results), "Some extractions failed"


def generate_summary_report(results: List[Dict[str, Any]]):
    """Generate a summary report of extraction results."""

    total_files = len(results)
    successful_extractions = len([r for r in results if r.get('extraction_success')])
    failed_extractions = total_files - successful_extractions

    # Calculate statistics for successful extractions
    successful_results = [r for r in results if r.get('extraction_success') and 'completeness_score' in r]

    if successful_results:
        avg_completeness = sum(r['completeness_score'] for r in successful_results) / len(successful_results)
        avg_field_count = sum(r['field_count'] for r in successful_results) / len(successful_results)

        # Method breakdown
        method_counts = {}
        for r in successful_results:
            method = r.get('extraction_method', 'unknown')
            method_counts[method] = method_counts.get(method, 0) + 1

        # Quality breakdown
        high_quality = len([r for r in successful_results if r['completeness_score'] > 0.8])
        medium_quality = len([r for r in successful_results if 0.5 <= r['completeness_score'] <= 0.8])
        low_quality = len([r for r in successful_results if r['completeness_score'] < 0.5])
    else:
        avg_completeness = 0
        avg_field_count = 0
        method_counts = {}
        high_quality = medium_quality = low_quality = 0

    print("=" * 60)
    print("📊 EXTRACTION SUMMARY REPORT")
    print("=" * 60)
    print(f"📁 Total files processed: {total_files}")
    print(f"✅ Successful extractions: {successful_extractions} ({successful_extractions/total_files*100:.1f}%)")
    print(f"❌ Failed extractions: {failed_extractions} ({failed_extractions/total_files*100:.1f}%)")
    print()

    if successful_results:
        print("📈 DATA QUALITY METRICS:")
        print(f"   Average completeness score: {avg_completeness:.3f}")
        print(f"   Average field count: {avg_field_count:.1f}")
        print()

        print("🔍 EXTRACTION METHODS:")
        for method, count in method_counts.items():
            print(f"   {method}: {count} files ({count/len(successful_results)*100:.1f}%)")
        print()

        print("⭐ QUALITY BREAKDOWN:")
        print(f"   High quality (>80%): {high_quality} files ({high_quality/len(successful_results)*100:.1f}%)")
        print(f"   Medium quality (50-80%): {medium_quality} files ({medium_quality/len(successful_results)*100:.1f}%)")
        print(f"   Low quality (<50%): {low_quality} files ({low_quality/len(successful_results)*100:.1f}%)")
        print()

    print("🎯 COMPARISON WITH ORIGINAL CRAWLER:")
    print("   Original completeness: ~25% (titles + URLs only)")
    print(f"   Enhanced completeness: {avg_completeness*100:.1f}% (comprehensive data)")
    print(f"   Improvement factor: {avg_completeness/0.25:.1f}x better")
    print()


def save_detailed_results(results: List[Dict[str, Any]]):
    """Save detailed extraction results to a JSON file."""

    output_file = "enhanced_extraction_results.json"

    output_data = {
        'metadata': {
            'test_script': 'test_enhanced_extraction.py',
            'test_time': datetime.now().isoformat(),
            'total_files': len(results),
            'successful_extractions': len([r for r in results if r.get('extraction_success')]),
        },
        'results': results
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"💾 Detailed results saved to: {output_file}")


def compare_with_original_data():
    """Compare enhanced extraction with original crypto_events.json."""

    original_file = "crypto_events.json"

    if not os.path.exists(original_file):
        print(f"⚠️  Original file {original_file} not found for comparison")
        return

    print("🔍 COMPARING WITH ORIGINAL DATA:")
    print("-" * 40)

    with open(original_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)

    original_events = original_data.get('events', [])

    print(f"📊 Original extraction results:")
    print(f"   Events: {len(original_events)}")

    # Analyze original data quality
    events_with_dates = len([e for e in original_events if e.get('date')])
    events_with_locations = len([e for e in original_events if e.get('location')])
    events_with_titles = len([e for e in original_events if e.get('title')])

    print(f"   Events with titles: {events_with_titles}/{len(original_events)} ({events_with_titles/len(original_events)*100:.1f}%)")
    print(f"   Events with dates: {events_with_dates}/{len(original_events)} ({events_with_dates/len(original_events)*100:.1f}%)")
    print(f"   Events with locations: {events_with_locations}/{len(original_events)} ({events_with_locations/len(original_events)*100:.1f}%)")

    # Show sample events
    print("\n📄 Sample original events:")
    for i, event in enumerate(original_events[:3]):
        print(f"   {i+1}. {event.get('title', 'No title')}")
        print(f"      Date: {event.get('date', 'No date')}")
        print(f"      Location: {event.get('location', 'No location')}")
        print(f"      URL: {event.get('url', 'No URL')}")
        print()


def main():
    """Main test function."""

    print("🧪 ENHANCED JSON EXTRACTION TEST")
    print("=" * 50)
    print()

    # Test extraction on HTML files
    test_extraction_on_html_files()

    # Compare with original data
    compare_with_original_data()

    print("✅ Test completed successfully!")
    print()
    print("💡 Next steps:")
    print("   1. Review the enhanced_extraction_results.json file")
    print("   2. Run the enhanced spider: scrapy crawl luma")
    print("   3. Compare the new crypto_events.json with the original")


if __name__ == "__main__":
    main()
