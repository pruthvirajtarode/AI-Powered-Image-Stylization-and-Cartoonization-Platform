"""
WhatsApp Business API Integration Module
Handles incoming messages, media downloads, image processing, and response sending
"""

import os
import json
import requests
import base64
import uuid
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WhatsAppProcessor:
    def __init__(self):
        """Initialize WhatsApp Business API configuration"""
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
        self.business_account_id = os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID', '')
        self.access_token = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
        self.verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN', 'toonify_webhook_token')
        
        self.api_url = f"https://graph.instagram.com/v18.0/{self.phone_number_id}/messages"
        self.media_url = "https://graph.instagram.com/v18.0"
        
        # Create media cache directory
        self.media_cache_dir = Path("data/whatsapp_media")
        self.media_cache_dir.mkdir(parents=True, exist_ok=True)
    
    def verify_webhook(self, token, challenge):
        """
        Verify webhook with WhatsApp (called by GET request from WhatsApp)
        
        Args:
            token: Verification token from WhatsApp
            challenge: Challenge string to echo back
            
        Returns:
            challenge if token matches, None otherwise
        """
        if token == self.verify_token:
            logger.info("WhatsApp webhook verified successfully")
            return challenge
        
        logger.warning(f"WhatsApp verification failed: invalid token {token}")
        return None
    
    def get_media_url(self, media_id):
        """
        Get download URL for media from WhatsApp
        
        Args:
            media_id: ID of the media file
            
        Returns:
            URL to download the media
        """
        try:
            url = f"{self.media_url}/{media_id}"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            media_data = response.json()
            return media_data.get('url')
        
        except Exception as e:
            logger.error(f"Failed to get media URL: {str(e)}")
            return None
    
    def download_media(self, media_url):
        """
        Download media file from WhatsApp
        
        Args:
            media_url: URL to download media from
            
        Returns:
            Path to the downloaded file or None
        """
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(media_url, headers=headers)
            response.raise_for_status()
            
            # Save media to cache
            media_filename = f"whatsapp_{uuid.uuid4().hex}.jpg"
            media_path = self.media_cache_dir / media_filename
            
            with open(media_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Media downloaded successfully: {media_path}")
            return str(media_path)
        
        except Exception as e:
            logger.error(f"Failed to download media: {str(e)}")
            return None
    
    def upload_media(self, image_path):
        """
        Upload processed image to WhatsApp media library
        
        Args:
            image_path: Path to the processed image
            
        Returns:
            Media ID for the uploaded image or None
        """
        try:
            url = f"{self.media_url}/{self.phone_number_id}/media"
            
            with open(image_path, 'rb') as image_file:
                files = {
                    'file': image_file,
                    'type': 'image/jpeg',
                    'messaging_product': 'whatsapp'
                }
                headers = {"Authorization": f"Bearer {self.access_token}"}
                
                response = requests.post(url, files=files, headers=headers, timeout=30)
                response.raise_for_status()
                
                media_data = response.json()
                media_id = media_data.get('id')
                
                logger.info(f"Media uploaded successfully: {media_id}")
                return media_id
        
        except Exception as e:
            logger.error(f"Failed to upload media: {str(e)}")
            return None
    
    def send_message(self, recipient_phone, message_text=None, media_id=None, media_type='image'):
        """
        Send text or media message via WhatsApp
        
        Args:
            recipient_phone: Phone number to send to (without + or country code prefix)
            message_text: Text message body
            media_id: ID of media to send
            media_type: Type of media (image, video, document, etc.)
            
        Returns:
            Message ID if successful, None otherwise
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Build message payload
            if message_text:
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": recipient_phone,
                    "type": "text",
                    "text": {"preview_url": True, "body": message_text}
                }
            elif media_id:
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": recipient_phone,
                    "type": media_type,
                    media_type: {"id": media_id}
                }
            else:
                logger.error("No message text or media provided")
                return None
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            message_data = response.json()
            message_id = message_data.get('messages', [{}])[0].get('id')
            
            logger.info(f"Message sent successfully: {message_id}")
            return message_id
        
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return None
    
    def handle_incoming_message(self, message_data):
        """
        Process incoming WhatsApp message
        
        Args:
            message_data: Message data from WhatsApp webhook
            
        Returns:
            Processing result dict
        """
        try:
            # Extract message info
            sender_phone = message_data.get('from')
            message_id = message_data.get('id')
            timestamp = message_data.get('timestamp')
            
            # Check if message contains media (image)
            if 'image' in message_data:
                media_id = message_data['image'].get('id')
                media_caption = message_data['image'].get('caption', 'Photo from WhatsApp')
                
                logger.info(f"Image received from {sender_phone}: {media_id}")
                
                # Get media URL
                media_url = self.get_media_url(media_id)
                if not media_url:
                    self.send_message(sender_phone, 
                        "❌ Sorry! Unable to download your image. Please try again.")
                    return {"success": False, "error": "Could not get media URL"}
                
                # Download media
                local_path = self.download_media(media_url)
                if not local_path:
                    self.send_message(sender_phone, 
                        "❌ Sorry! Failed to process your image. Please try again.")
                    return {"success": False, "error": "Could not download media"}
                
                # Return processing info
                return {
                    "success": True,
                    "type": "image",
                    "sender_phone": sender_phone,
                    "message_id": message_id,
                    "timestamp": timestamp,
                    "media_id": media_id,
                    "local_path": local_path,
                    "caption": media_caption
                }
            
            elif 'text' in message_data:
                text_body = message_data['text'].get('body', '')
                logger.info(f"Text message received from {sender_phone}: {text_body[:50]}")
                
                # Send help message
                help_text = """👋 Welcome to Toonify AI!

🎨 Send me a photo and I'll transform it into beautiful cartoon art!

📸 Just upload an image and I'll apply stunning stylization effects.

🚀 Powered by AI Image Stylization Technology

Need help? Visit: https://toonify-ai-saas.onrender.com"""
                
                self.send_message(sender_phone, help_text)
                
                return {
                    "success": True,
                    "type": "text",
                    "sender_phone": sender_phone,
                    "message_id": message_id,
                    "text": text_body
                }
            
            else:
                logger.warning(f"Unhandled message type from {sender_phone}")
                self.send_message(sender_phone, 
                    "📸 Please send me an image to stylize!")
                
                return {
                    "success": False,
                    "error": "Unhandled message type"
                }
        
        except Exception as e:
            logger.error(f"Error handling incoming message: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_stylized_image(self, recipient_phone, processed_image_path, style_name="Cartoon"):
        """
        Send stylized image back to user via WhatsApp
        
        Args:
            recipient_phone: Phone number of recipient
            processed_image_path: Path to processed image
            style_name: Name of applied style
            
        Returns:
            Message ID if successful, None otherwise
        """
        try:
            # Upload processed image to WhatsApp media
            media_id = self.upload_media(processed_image_path)
            if not media_id:
                logger.error("Failed to upload processed image")
                self.send_message(recipient_phone, 
                    "❌ Failed to send your stylized image. Please try again.")
                return None
            
            # Send the image with caption
            caption = f"✨ Your {style_name} Style Photo\n\n🎨 Powered by Toonify AI\n📱 Download high quality: https://toonify-ai-saas.onrender.com"
            
            # WhatsApp doesn't support captions for images in the media object,
            # so send text message first, then image
            self.send_message(recipient_phone, caption)
            
            # Send the image
            message_id = self.send_message(recipient_phone, 
                media_id=media_id, 
                media_type='image')
            
            if message_id:
                logger.info(f"Stylized image sent successfully to {recipient_phone}")
                return message_id
            
        except Exception as e:
            logger.error(f"Failed to send stylized image: {str(e)}")
        
        return None


# Global instance
whatsapp_processor = WhatsAppProcessor()
