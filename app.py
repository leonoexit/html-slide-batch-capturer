"""
Batch HTML Slide Screenshot Capture Tool
========================================
Author: Senior Python Automation Engineer
Description: Automatically captures screenshots of all slides from multiple HTML files

Installation:
    pip install playwright
    playwright install chromium

Usage:
    python capture_all.py
"""

import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import time


class SlideCaptureBatchProcessor:
    """Handles batch processing of HTML slide files for screenshot capture"""

    def __init__(self, source_dir: str = ".", output_base_dir: str = "output_images"):
        """
        Initialize the batch processor

        Args:
            source_dir: Directory to scan for HTML files (default: current directory)
            output_base_dir: Base directory for output images (default: output_images)
        """
        self.source_dir = Path(source_dir).resolve()
        self.output_base_dir = Path(output_base_dir).resolve()
        self.html_files = []
        self.global_slide_counter = 0  # Counter tuyến tính cho tất cả slides

    def scan_html_files(self):
        """Scan source directory for all HTML files"""
        print(f"\n{'='*60}")
        print(f"SCANNING DIRECTORY: {self.source_dir}")
        print(f"{'='*60}")

        self.html_files = sorted(self.source_dir.glob("*.html"))

        if not self.html_files:
            print("No HTML files found in the directory.")
            return False

        print(f"\nFound {len(self.html_files)} HTML file(s):")
        for idx, file in enumerate(self.html_files, 1):
            print(f"  [{idx}] {file.name}")

        return True

    def capture_slides_from_file(self, html_file: Path, browser) -> int:
        """
        Capture all slides from a single HTML file

        Args:
            html_file: Path to the HTML file
            browser: Playwright browser instance

        Returns:
            Number of slides captured from this file
        """
        print(f"\n{'─'*60}")
        print(f"Processing: {html_file.name}")
        print(f"{'─'*60}")

        # Create new page
        page = browser.new_page(device_scale_factor=2)
        slides_captured = 0

        try:
            # Convert to absolute file URL
            file_url = html_file.as_uri()
            print(f"Loading: {file_url}")

            # Navigate to the HTML file
            page.goto(file_url)

            # Wait for resources to load
            print("Waiting for page to render (3 seconds)...")
            page.wait_for_timeout(3000)

            # Find all slide elements
            slides = page.locator(".slide").all()
            slide_count = len(slides)

            if slide_count == 0:
                print("WARNING: No slides found with class '.slide'")
                return 0

            print(f"Found {slide_count} slide(s). Starting capture...\n")

            # Capture each slide
            for idx, slide in enumerate(slides, 1):
                # Tăng counter toàn cục
                self.global_slide_counter += 1
                
                # Đặt tên file chỉ bằng số (01.png, 02.png, ...)
                filename = f"{self.global_slide_counter:02d}.png"
                output_path = self.output_base_dir / filename

                # Take screenshot of the slide element
                slide.screenshot(path=str(output_path))

                # Progress indicator
                print(f"  [{idx}/{slide_count}] Captured: {filename}")
                slides_captured += 1

            print(f"\nCompleted: {html_file.name}")
            print(f"Slides captured from this file: {slide_count}")

        except Exception as e:
            print(f"ERROR processing {html_file.name}: {str(e)}")

        finally:
            # Close the page
            page.close()

        return slides_captured

    def process_all(self):
        """Main processing method - batch process all HTML files"""
        start_time = time.time()

        # Scan for HTML files
        if not self.scan_html_files():
            return

        # Create output directory (tất cả ảnh vào chung 1 folder)
        self.output_base_dir.mkdir(parents=True, exist_ok=True)

        # Reset counter
        self.global_slide_counter = 0

        print(f"\n{'='*60}")
        print(f"STARTING BATCH PROCESSING")
        print(f"Output folder: {self.output_base_dir}")
        print(f"{'='*60}")

        # Launch browser
        with sync_playwright() as p:
            print("\nLaunching Chromium browser (headless mode)...")
            browser = p.chromium.launch(headless=True)

            try:
                # Process each HTML file
                for idx, html_file in enumerate(self.html_files, 1):
                    print(f"\n[File {idx}/{len(self.html_files)}]")
                    self.capture_slides_from_file(html_file, browser)

            finally:
                # Close browser
                browser.close()

        # Summary
        elapsed_time = time.time() - start_time

        print(f"\n{'='*60}")
        print(f"BATCH PROCESSING COMPLETED")
        print(f"{'='*60}")
        print(f"Total HTML files processed: {len(self.html_files)}")
        print(f"Total slides captured: {self.global_slide_counter}")
        print(f"Output directory: {self.output_base_dir}")
        print(f"Files: 01.png -> {self.global_slide_counter:02d}.png")
        print(f"Time elapsed: {elapsed_time:.2f} seconds")
        print(f"{'='*60}\n")


def main():
    """Entry point of the script"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   Batch HTML Slide Screenshot Capture Tool              ║
    ║   Powered by Playwright                                  ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # Initialize and run the batch processor
    processor = SlideCaptureBatchProcessor(
        source_dir=".",  # Current directory
        output_base_dir="output_images"
    )

    processor.process_all()


if __name__ == "__main__":
    main()