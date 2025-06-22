#!/usr/bin/env python3
"""
Yochi Price Monitor for Coles Australia
Monitors product prices and sends notifications when discounts are found.
"""

import json
import logging
import os
import re
import smtplib
import subprocess
import sys
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup


class PriceMonitor:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.price_history_file = self.config.get("price_history_file", "price_history.json")
        self.setup_logging()
        self.price_history = self.load_price_history()
        self.current_deal_info = None  # Store current deal information

    def load_config(self) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.create_default_config()
            with open(self.config_file, 'r') as f:
                return json.load(f)

    def create_default_config(self):
        """Create default configuration file."""
        default_config = {
            "url": "https://www.coles.com.au/search/products?q=yochi",
            "discount_threshold": 0.30,
            "regular_price": None,
            "check_interval_minutes": 60,
            "price_history_file": "price_history.json",
            "notifications": {
                "macos_enabled": True,
                "email_enabled": False,
                "telegram_enabled": False
            },
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "",
                "sender_name": "Price Monitor"
            },
            "telegram": {
                "bot_token": "",
                "chat_id": ""
            },
            "logging": {
                "level": "INFO",
                "file": "price_monitor.log"
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        
        print(f"Created default config file: {self.config_file}")
        print("Please edit the configuration file before running the monitor.")

    def setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, self.config.get("logging", {}).get("level", "INFO"))
        log_file = self.config.get("logging", {}).get("file", "price_monitor.log")
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_price_history(self) -> List[Dict]:
        """Load price history from JSON file."""
        try:
            with open(self.price_history_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_price_history(self):
        """Save price history to JSON file."""
        with open(self.price_history_file, 'w') as f:
            json.dump(self.price_history, f, indent=2)

    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for web scraping."""
        return {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def scrape_all_yochi_products(self, test_mode: bool = False) -> List[Dict]:
        """
        Scrape all Yochi products from Coles search results.
        Returns list of {'name': str, 'price': float} or empty list if failed.
        """
        if test_mode:
            # Return mock data for testing - multiple products
            return [
                {"name": "Yo Chi Frozen Natural Yoghurt | 500mL", "price": 4.50},
                {"name": "Yo Chi Frozen Wild Berry Yoghurt | 500mL", "price": 3.80},
                {"name": "Yo Chi Frozen Mango Yoghurt | 500mL", "price": 4.20},
                {"name": "Yo Chi Frozen Vanilla Yoghurt | 500mL", "price": 4.00}
            ]

        try:
            response = requests.get(
                self.config["url"],
                headers=self.get_headers(),
                timeout=30
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Try to find product containers - Coles uses various structures
            product_containers = []
            
            # Different container selectors to try
            container_selectors = [
                '[data-testid="product-tile"]',
                '.product-tile',
                '.product-item',
                '.search-results .product',
                'article'
            ]
            
            for selector in container_selectors:
                containers = soup.select(selector)
                if containers:
                    product_containers = containers
                    self.logger.info(f"Found {len(containers)} product containers using selector: {selector}")
                    break
            
            if not product_containers:
                self.logger.warning("No product containers found")
                return []
            
            # Extract price and name from each container
            for container in product_containers:
                try:
                    # Try to find product name within this container
                    name_selectors = [
                        '[data-testid="product-name"]',
                        '.product__title',
                        '.product-name',
                        'h3 a',
                        'h3',
                        'h2 a',
                        'h2',
                        '.product-title',
                        'a[href*="product"]'
                    ]
                    
                    product_name = None
                    for selector in name_selectors:
                        name_element = container.select_one(selector)
                        if name_element:
                            product_name = name_element.get_text(strip=True)
                            if 'yochi' in product_name.lower() or 'yo chi' in product_name.lower():
                                break
                            else:
                                product_name = None
                    
                    if not product_name:
                        continue  # Skip if not a Yochi product
                    
                    # Try to find price within this container
                    price_selectors = [
                        '[data-testid="price-per-item"]',
                        '.price__value',
                        '.price-per-item',
                        '.price',
                        '.coles-price',
                        '[class*="price"]'
                    ]
                    
                    price = None
                    for selector in price_selectors:
                        price_element = container.select_one(selector)
                        if price_element:
                            price_text = price_element.get_text(strip=True)
                            # Extract numeric price
                            price_match = re.search(r'[\d.]+', price_text.replace('$', '').replace(',', ''))
                            if price_match:
                                price = float(price_match.group())
                                break
                    
                    if price and product_name:
                        products.append({
                            "name": product_name,
                            "price": price
                        })
                        self.logger.info(f"Found Yochi product: {product_name} - ${price}")
                
                except Exception as e:
                    self.logger.debug(f"Error parsing product container: {e}")
                    continue
            
            if not products:
                self.logger.warning("No Yochi products found with valid prices")
            else:
                self.logger.info(f"Successfully scraped {len(products)} Yochi products")
            
            return products
            
        except requests.RequestException as e:
            self.logger.error(f"Network error while scraping: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error scraping Yochi products: {e}")
            return []

    def find_best_deal(self, products: List[Dict]) -> Optional[Dict]:
        """
        Find the cheapest product and return deal info.
        Returns dict with best deal info or None if no products.
        """
        if not products:
            return None
        
        # Sort by price to find cheapest
        sorted_products = sorted(products, key=lambda x: x['price'])
        cheapest = sorted_products[0]
        
        # Create alternatives list (other products)
        alternatives = [
            f"{p['name'].split('|')[0].replace('Yo Chi Frozen', '').strip()} ${p['price']:.2f}"
            for p in sorted_products[1:4]  # Show up to 3 alternatives
        ]
        
        return {
            "cheapest_product": cheapest,
            "all_products": products,
            "alternatives": alternatives
        }

    def scrape_price(self, test_mode: bool = False) -> Optional[Tuple[float, str]]:
        """
        Scrape prices and return the best deal.
        Returns tuple of (cheapest_price, product_name) or None if failed.
        """
        products = self.scrape_all_yochi_products(test_mode)
        
        if not products:
            self.logger.warning("No Yochi products found")
            return None
        
        deal_info = self.find_best_deal(products)
        if not deal_info:
            return None
        
        cheapest = deal_info["cheapest_product"]
        
        # Store deal info for use in notifications
        self.current_deal_info = deal_info
        
        return (cheapest["price"], cheapest["name"])

    def calculate_regular_price(self) -> Optional[float]:
        """Calculate regular price from price history."""
        if not self.price_history:
            return self.config.get("regular_price")
        
        # Use the highest price from the last 30 days as regular price
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_prices = [
            entry["price"] for entry in self.price_history
            if datetime.fromisoformat(entry["timestamp"]) > thirty_days_ago
        ]
        
        if recent_prices:
            regular_price = max(recent_prices)
            self.logger.info(f"Calculated regular price from history: ${regular_price}")
            return regular_price
        
        return self.config.get("regular_price")

    def is_discounted(self, current_price: float) -> Tuple[bool, Optional[float]]:
        """Check if current price represents a discount."""
        regular_price = self.calculate_regular_price()
        
        if regular_price is None:
            self.logger.warning("No regular price available for comparison")
            return False, None
        
        discount_percentage = (regular_price - current_price) / regular_price
        threshold = self.config["discount_threshold"]
        
        is_discount = discount_percentage >= threshold
        
        if is_discount:
            self.logger.info(f"Discount found! {discount_percentage:.1%} off (${current_price} vs ${regular_price})")
        
        return is_discount, discount_percentage

    def request_notification_permission(self):
        """Request notification permission on macOS."""
        try:
            # This will trigger the permission request dialog
            applescript = '''
            try
                display notification "Permission test" with title "Yochi Price Monitor" 
            on error
                display dialog "Please allow notifications for this app in System Preferences → Security & Privacy → Privacy → Notifications" buttons {"OK"} default button 1
            end try
            '''
            subprocess.run(["osascript", "-e", applescript], capture_output=True, timeout=10)
        except Exception:
            pass  # Ignore errors during permission request

    def send_macos_notification(self, title: str, message: str, sound: bool = True):
        """Send persistent macOS notification."""
        if not self.config.get("notifications", {}).get("macos_enabled", True):
            return
        
        try:
            # Use a more reliable AppleScript approach that requests permissions
            sound_option = "sound name \"default\"" if sound else ""
            applescript = f'''
            try
                display notification "{message}" with title "{title}" {sound_option}
            on error
                display dialog "Notification: {title}\\n{message}" buttons {{"OK"}} default button 1
            end try
            '''
            
            result = subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info(f"macOS notification sent: {title}")
            else:
                self.logger.warning(f"Notification may have failed, using fallback: {result.stderr}")
                # Fallback to terminal bell and print
                print(f"\n🔔 {title}: {message}\n")
                subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], 
                             capture_output=True, timeout=5)
            
        except subprocess.TimeoutExpired:
            self.logger.warning("Notification timed out, using fallback")
            print(f"\n🔔 {title}: {message}\n")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to send macOS notification: {e}")
            print(f"\n🔔 {title}: {message}\n")
        except Exception as e:
            self.logger.error(f"Error sending macOS notification: {e}")
            print(f"\n🔔 {title}: {message}\n")

    def send_email_notification(self, subject: str, body: str):
        """Send email notification via Gmail SMTP."""
        if not self.config.get("notifications", {}).get("email_enabled", False):
            return
        
        email_config = self.config.get("email", {})
        sender_email = email_config.get("sender_email")
        
        if not sender_email:
            self.logger.warning("Email notifications enabled but no sender email configured")
            return
        
        # Get password from environment variable
        password = os.environ.get("GMAIL_APP_PASSWORD")
        if not password:
            self.logger.error("GMAIL_APP_PASSWORD environment variable not set")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{email_config.get('sender_name', 'Price Monitor')} <{sender_email}>"
            msg['To'] = sender_email  # Send to self
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(email_config.get("smtp_server", "smtp.gmail.com"), 
                                email_config.get("smtp_port", 587))
            server.starttls()
            server.login(sender_email, password)
            
            text = msg.as_string()
            server.sendmail(sender_email, sender_email, text)
            server.quit()
            
            self.logger.info("Email notification sent successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")

    def send_telegram_notification(self, message: str):
        """Send Telegram notification."""
        if not self.config.get("notifications", {}).get("telegram_enabled", False):
            return
        
        telegram_config = self.config.get("telegram", {})
        bot_token = telegram_config.get("bot_token")
        chat_id = telegram_config.get("chat_id")
        
        if not bot_token or not chat_id:
            self.logger.warning("Telegram notifications enabled but bot_token or chat_id not configured")
            return
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.logger.info("Telegram notification sent successfully")
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to send Telegram notification - Network error: {e}")
        except Exception as e:
            self.logger.error(f"Failed to send Telegram notification: {e}")

    def record_price(self, price: float, product_name: str, is_discount: bool = False):
        """Record price in history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "price": price,
            "product_name": product_name,
            "is_discount": is_discount
        }
        
        self.price_history.append(entry)
        
        # Keep only last 1000 entries
        if len(self.price_history) > 1000:
            self.price_history = self.price_history[-1000:]
        
        self.save_price_history()

    def check_price(self, test_mode: bool = False):
        """Main price checking function."""
        self.logger.info("Starting price check...")
        
        price_data = self.scrape_price(test_mode)
        if price_data is None:
            self.logger.error("Failed to get price data")
            return
        
        current_price, product_name = price_data
        is_discount_found, discount_percentage = self.is_discounted(current_price)
        
        # Record the price
        self.record_price(current_price, product_name, is_discount_found)
        
        if is_discount_found:
            discount_percent = f"{discount_percentage:.1%}"
            
            # Extract product flavor for cleaner display
            product_flavor = product_name.split('|')[0].replace('Yo Chi Frozen', '').strip()
            
            title = f"🎉 Best Yochi Deal Found!"
            message = f"{product_flavor}\nNow ${current_price} ({discount_percent} off!)"
            
            # Send notifications
            self.send_macos_notification(title, message)
            
            # Enhanced email with alternatives
            alternatives_text = ""
            if self.current_deal_info and self.current_deal_info.get("alternatives"):
                alternatives_text = "\nOther options available:\n" + "\n".join(
                    f"• {alt}" for alt in self.current_deal_info["alternatives"]
                )
            
            email_subject = f"Best Yochi Deal - {discount_percent} Off!"
            email_body = f"""
🎉 Great news! Best Yochi deal found at Coles!

🏆 BEST DEAL: {product_flavor}
💰 Price: ${current_price}
🔥 Discount: {discount_percent} off!
{alternatives_text}

🛒 Shop now: {self.config['url']}

Happy shopping!
            """.strip()
            
            self.send_email_notification(email_subject, email_body)
            
            # Enhanced Telegram notification with alternatives
            alternatives_telegram = ""
            if self.current_deal_info and self.current_deal_info.get("alternatives"):
                alternatives_telegram = "\n\n📋 <b>Other options:</b>\n" + "\n".join(
                    f"• {alt}" for alt in self.current_deal_info["alternatives"]
                )
            
            telegram_message = f"""
🎉 <b>Best Yochi Deal Found!</b>

🏆 <b>BEST DEAL:</b> {product_flavor}
💰 <b>Price:</b> ${current_price}
🔥 <b>Discount:</b> {discount_percent} off!
{alternatives_telegram}

<a href="{self.config['url']}">🛒 Shop Now at Coles</a>

Happy shopping! 🛍️
            """.strip()
            
            self.send_telegram_notification(telegram_message)
        else:
            self.logger.info(f"No significant discount found. Current price: ${current_price}")

    def run_once(self, test_mode: bool = False):
        """Run price check once."""
        try:
            self.check_price(test_mode)
        except Exception as e:
            self.logger.error(f"Error during price check: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Yochi Price Monitor")
    parser.add_argument("--config", default="config.json", help="Configuration file path")
    parser.add_argument("--test", action="store_true", help="Run in test mode with mock data")
    parser.add_argument("--test-notifications", action="store_true", help="Test notification systems")
    parser.add_argument("--request-permissions", action="store_true", help="Request notification permissions")
    
    args = parser.parse_args()
    
    monitor = PriceMonitor(args.config)
    
    if args.request_permissions:
        print("Requesting notification permissions...")
        monitor.request_notification_permission()
        print("If a dialog appeared, please allow notifications.")
        print("Then check System Preferences → Notifications for 'osascript' or 'Terminal'")
        return
    
    if args.test_notifications:
        print("Testing macOS notification...")
        monitor.send_macos_notification("Test Notification", "This is a test message")
        
        print("Testing email notification...")
        monitor.send_email_notification("Test Email", "This is a test email from Price Monitor")
        
        print("Testing Telegram notification...")
        monitor.send_telegram_notification("🤖 <b>Test Message</b>\n\nThis is a test message from Yochi Price Monitor!")
        
        return
    
    monitor.run_once(test_mode=args.test)


if __name__ == "__main__":
    main()