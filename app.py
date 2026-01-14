"""
Batch HTML Slide Screenshot Capture Tool
========================================
Author: Senior Python Automation Engineer
Description: Automatically captures screenshots of all slides from multiple HTML files
             with auto-detection of slide class names

Installation:
    pip install playwright
    playwright install chromium

Usage:
    # Interactive mode
    python capture_all.py
    
    # With arguments
    python capture_all.py --input "./slides" --output "./images"
    python capture_all.py -i "./slides" -o "./images"
"""

import os
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, Page
import time
from collections import Counter


def get_user_input_paths():
    """
    Hỏi user nhập đường dẫn input/output
    
    Returns:
        tuple: (source_dir, output_dir)
    """
    print("\n📁 Thiết lập đường dẫn:")
    print("─" * 60)
    
    # Nhập đường dẫn input
    while True:
        source = input("Nhập đường dẫn thư mục chứa file HTML (Enter = thư mục hiện tại): ").strip()
        
        if not source:
            source = "."
        
        source_path = Path(source).resolve()
        
        if not source_path.exists():
            print(f"❌ Đường dẫn không tồn tại: {source_path}")
            print("Vui lòng nhập lại.\n")
            continue
        
        if not source_path.is_dir():
            print(f"❌ Đây không phải thư mục: {source_path}")
            print("Vui lòng nhập lại.\n")
            continue
        
        print(f"✅ Thư mục input: {source_path}")
        break
    
    # Nhập đường dẫn output
    output = input("Nhập đường dẫn thư mục lưu ảnh (Enter = 'output_images'): ").strip()
    
    if not output:
        output = "output_images"
    
    output_path = Path(output).resolve()
    print(f"✅ Thư mục output: {output_path}")
    
    return str(source_path), str(output_path)


def parse_arguments():
    """
    Parse command line arguments
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Batch capture screenshots from HTML slide files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python capture_all.py
  
  # With arguments
  python capture_all.py --input "./slides" --output "./images"
  python capture_all.py -i "./slides" -o "./images"
        """
    )
    
    parser.add_argument(
        "-i", "--input",
        type=str,
        default=None,
        help="Đường dẫn thư mục chứa file HTML (default: hỏi user)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Đường dẫn thư mục lưu ảnh (default: hỏi user hoặc 'output_images')"
    )
    
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Không hỏi user, dùng default values"
    )
    
    return parser.parse_args()


def validate_directory(path: str, dir_type: str = "input") -> Path:
    """
    Validate đường dẫn thư mục
    
    Args:
        path: Đường dẫn cần validate
        dir_type: Loại thư mục ('input' hoặc 'output')
    
    Returns:
        Path: Validated path object
    
    Raises:
        ValueError: Nếu đường dẫn không hợp lệ
    """
    path_obj = Path(path).resolve()
    
    if dir_type == "input":
        if not path_obj.exists():
            raise ValueError(f"Thư mục input không tồn tại: {path_obj}")
        if not path_obj.is_dir():
            raise ValueError(f"Đây không phải thư mục: {path_obj}")
    
    return path_obj


def detect_slide_class(page: Page) -> tuple[str, int]:
    """
    Auto-detect slide class name bằng cách phân tích cấu trúc HTML
    
    Strategy:
    1. Tìm tất cả div trong body
    2. Lấy class đầu tiên của mỗi div
    3. Tìm class xuất hiện nhiều lần nhất (likely là slide class)
    4. Validate bằng cách check số lượng elements
    
    Args:
        page: Playwright page instance
    
    Returns:
        tuple: (class_name, element_count) hoặc (None, 0) nếu không tìm được
    """
    print("\n🔍 Auto-detecting slide class name...")
    
    try:
        # Lấy tất cả các class name từ body > div (hoặc các container chính)
        # JavaScript để lấy class đầu tiên của các div
        class_analysis = page.evaluate("""
            () => {
                // Lấy tất cả div trong body
                const divs = document.querySelectorAll('body > div, body > div > div, body > main > div');
                const classMap = {};
                
                divs.forEach(div => {
                    // Lấy class đầu tiên (nếu có)
                    if (div.classList.length > 0) {
                        const firstClass = div.classList[0];
                        classMap[firstClass] = (classMap[firstClass] || 0) + 1;
                    }
                });
                
                return classMap;
            }
        """)
        
        if not class_analysis:
            print("   ⚠️  No div with classes found")
            return None, 0
        
        print(f"   📊 Class distribution:")
        for cls, count in sorted(class_analysis.items(), key=lambda x: x[1], reverse=True):
            print(f"      .{cls}: {count} elements")
        
        # Tìm class xuất hiện nhiều nhất
        most_common_class = max(class_analysis.items(), key=lambda x: x[1])
        class_name, count = most_common_class
        
        # Validate: phải có ít nhất 2 elements cùng class
        if count < 2:
            print(f"   ⚠️  Class '.{class_name}' only has {count} element(s)")
            print("   💡 Trying alternative detection methods...")
            
            # Alternative: tìm bất kỳ elements nào có pattern giống slide
            alternative_selectors = [
                'section', 
                '[class*="slide"]', 
                '[class*="page"]',
                '[class*="screen"]',
                'body > div'
            ]
            
            for selector in alternative_selectors:
                elements = page.locator(selector).all()
                if len(elements) >= 2:
                    print(f"   ✅ Found {len(elements)} elements with selector: {selector}")
                    return selector, len(elements)
            
            return None, 0
        
        print(f"   ✅ Detected slide class: '.{class_name}' ({count} elements)")
        return f".{class_name}", count
        
    except Exception as e:
        print(f"   ❌ Error during detection: {str(e)}")
        return None, 0


def get_slide_selector_with_fallback(page: Page) -> tuple[str, int]:
    """
    Lấy slide selector với fallback strategies
    
    Args:
        page: Playwright page instance
    
    Returns:
        tuple: (selector, count)
    """
    # Strategy 1: Auto-detect từ class name
    selector, count = detect_slide_class(page)
    
    if selector and count > 0:
        return selector, count
    
    # Strategy 2: Thử các common selectors
    print("\n🔄 Trying common slide selectors...")
    common_selectors = [
        '.slide',
        '.slides',
        'section',
        '.page',
        '.screen',
        '[class*="slide"]',
        'body > div > div'
    ]
    
    for selector in common_selectors:
        try:
            elements = page.locator(selector).all()
            if len(elements) > 0:
                print(f"   ✅ Found {len(elements)} elements with: {selector}")
                return selector, len(elements)
        except:
            continue
    
    print("   ❌ No suitable selector found")
    return None, 0


class SlideCaptureBatchProcessor:
    """Handles batch processing of HTML slide files for screenshot capture"""

    def __init__(self, source_dir: str = ".", output_base_dir: str = "output_images"):
        """
        Initialize the batch processor

        Args:
            source_dir: Directory to scan for HTML files
            output_base_dir: Base directory for output images
        """
        self.source_dir = Path(source_dir).resolve()
        self.output_base_dir = Path(output_base_dir).resolve()
        self.html_files = []
        self.global_slide_counter = 0

    def scan_html_files(self):
        """Scan source directory for all HTML files"""
        print(f"\n{'='*60}")
        print(f"SCANNING DIRECTORY: {self.source_dir}")
        print(f"{'='*60}")

        self.html_files = sorted(self.source_dir.glob("*.html"))

        if not self.html_files:
            print("❌ Không tìm thấy file HTML nào trong thư mục.")
            return False

        print(f"\n✅ Tìm thấy {len(self.html_files)} file HTML:")
        for idx, file in enumerate(self.html_files, 1):
            print(f"  [{idx}] {file.name}")

        return True

    def capture_slides_from_file(self, html_file: Path, browser) -> int:
        """
        Capture all slides from a single HTML file with auto-detection
        
        Args:
            html_file: Path to the HTML file
            browser: Playwright browser instance
        
        Returns:
            Number of slides captured from this file
        """
        print(f"\n{'─'*60}")
        print(f"Processing: {html_file.name}")
        print(f"{'─'*60}")

        page = browser.new_page(device_scale_factor=2)
        slides_captured = 0

        try:
            # Load HTML file
            file_url = html_file.as_uri()
            print(f"Loading: {file_url}")
            page.goto(file_url)
            
            print("Waiting for page to render (3 seconds)...")
            page.wait_for_timeout(3000)

            # Auto-detect slide selector
            selector, slide_count = get_slide_selector_with_fallback(page)
            
            if not selector or slide_count == 0:
                print("❌ Cannot find slide elements in this file")
                return 0

            print(f"\n📸 Starting capture with selector: {selector}")
            print(f"   Found {slide_count} slide(s)\n")

            # Capture slides
            slides = page.locator(selector).all()
            
            for idx, slide in enumerate(slides, 1):
                self.global_slide_counter += 1
                filename = f"{self.global_slide_counter:02d}.png"
                output_path = self.output_base_dir / filename

                slide.screenshot(path=str(output_path))
                print(f"  ✓ [{idx}/{slide_count}] Captured: {filename}")
                slides_captured += 1

            print(f"\n✅ Completed: {html_file.name}")
            print(f"   Slides captured: {slide_count}")

        except Exception as e:
            print(f"❌ ERROR processing {html_file.name}: {str(e)}")

        finally:
            page.close()

        return slides_captured

    def process_all(self):
        """Main processing method - batch process all HTML files"""
        start_time = time.time()

        if not self.scan_html_files():
            return

        self.output_base_dir.mkdir(parents=True, exist_ok=True)
        self.global_slide_counter = 0

        print(f"\n{'='*60}")
        print(f"🚀 STARTING BATCH PROCESSING")
        print(f"Output folder: {self.output_base_dir}")
        print(f"{'='*60}")

        with sync_playwright() as p:
            print("\n🌐 Launching Chromium browser (headless mode)...")
            browser = p.chromium.launch(headless=True)

            try:
                for idx, html_file in enumerate(self.html_files, 1):
                    print(f"\n[File {idx}/{len(self.html_files)}]")
                    self.capture_slides_from_file(html_file, browser)

            finally:
                browser.close()

        elapsed_time = time.time() - start_time

        print(f"\n{'='*60}")
        print(f"✅ BATCH PROCESSING COMPLETED")
        print(f"{'='*60}")
        print(f"📊 Total HTML files processed: {len(self.html_files)}")
        print(f"📸 Total slides captured: {self.global_slide_counter}")
        print(f"📁 Output directory: {self.output_base_dir}")
        print(f"📄 Files: 01.png -> {self.global_slide_counter:02d}.png")
        print(f"⏱️  Time elapsed: {elapsed_time:.2f} seconds")
        print(f"{'='*60}\n")


def main():
    """Entry point of the script"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   Batch HTML Slide Screenshot Capture Tool              ║
    ║   Powered by Playwright                                  ║
    ║   🇻🇳 Vietnamese Edition - Auto Class Detection          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    args = parse_arguments()
    
    if args.input and args.output:
        source_dir = args.input
        output_dir = args.output
        print(f"📂 Using command line arguments:")
        print(f"   Input:  {source_dir}")
        print(f"   Output: {output_dir}")
        
        try:
            validate_directory(source_dir, "input")
        except ValueError as e:
            print(f"\n❌ Error: {e}")
            return
            
    elif args.no_interactive:
        source_dir = "."
        output_dir = "output_images"
        print(f"📂 Using default paths:")
        print(f"   Input:  {source_dir}")
        print(f"   Output: {output_dir}")
        
    else:
        source_dir, output_dir = get_user_input_paths()

    processor = SlideCaptureBatchProcessor(
        source_dir=source_dir,
        output_base_dir=output_dir
    )

    processor.process_all()


if __name__ == "__main__":
    main()
