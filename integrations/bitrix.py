import requests
import logging
from typing import Optional, Dict, List
from config import BITRIX_WEBHOOK_URL, BITRIX_CATEGORY_ID

logger = logging.getLogger(__name__)


class BitrixClient:
    def __init__(self):
        self.webhook_url = BITRIX_WEBHOOK_URL
        self.category_id = BITRIX_CATEGORY_ID

    def _make_request(self, method: str, params: Dict = None) -> Optional[Dict]:
        """Make request to Bitrix24 API"""
        try:
            url = f"{self.webhook_url}{method}"
            response = requests.post(url, json=params or {}, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'error' in data:
                logger.error(f"Bitrix API error: {data['error']}")
                return None

            return data.get('result')
        except requests.exceptions.RequestException as e:
            logger.error(f"Bitrix request error: {e}")
            return None

    def find_contact_by_phone(self, phone: str) -> Optional[Dict]:
        """Find contact in Bitrix24 by phone number"""
        # Clean phone number
        phone_clean = phone.replace('+', '').replace(' ', '').replace('-', '')

        params = {
            'filter': {'PHONE': phone_clean},
            'select': ['ID', 'NAME', 'LAST_NAME', 'PHONE']
        }

        result = self._make_request('crm.contact.list', params)

        if result and len(result) > 0:
            return result[0]

        return None

    def get_deals_by_contact(self, contact_id: int) -> List[Dict]:
        """Get all deals for contact in specific category"""
        params = {
            'filter': {
                'CONTACT_ID': contact_id,
                'CATEGORY_ID': self.category_id
            },
            'select': ['ID', 'TITLE', 'STAGE_ID', 'OPPORTUNITY', 'CURRENCY_ID']
        }

        result = self._make_request('crm.deal.list', params)

        return result if result else []

    def get_deal(self, deal_id: int) -> Optional[Dict]:
        """Get deal by ID"""
        params = {'id': deal_id}
        result = self._make_request('crm.deal.get', params)
        return result

    def update_deal_field(self, deal_id: int, field_name: str, value: str) -> bool:
        """Update specific field in deal"""
        params = {
            'id': deal_id,
            'fields': {field_name: value}
        }

        result = self._make_request('crm.deal.update', params)
        return result is not None

    def update_deal_custom_field(self, deal_id: int, field_code: str, value: str) -> bool:
        """Update custom field (UF_*) in deal"""
        return self.update_deal_field(deal_id, field_code, value)

    def find_client_in_funnel(self, phone: str) -> Optional[Dict]:
        """
        Find client in Bitrix24 by phone and check if they have deal in category 7
        Returns dict with contact_id, deal_id, and current_stage or None
        """
        # Find contact
        contact = self.find_contact_by_phone(phone)
        if not contact:
            logger.info(f"Contact not found for phone: {phone}")
            return None

        contact_id = contact['ID']
        logger.info(f"Found contact ID: {contact_id}")

        # Get deals in category 7
        deals = self.get_deals_by_contact(contact_id)
        if not deals:
            logger.info(f"No deals found in category {self.category_id} for contact {contact_id}")
            return None

        # Take first active deal
        deal = deals[0]
        logger.info(f"Found deal ID: {deal['ID']} with stage: {deal['STAGE_ID']}")

        return {
            'contact_id': contact_id,
            'deal_id': deal['ID'],
            'current_stage': deal['STAGE_ID'],
            'contact_name': f"{contact.get('NAME', '')} {contact.get('LAST_NAME', '')}".strip()
        }


# Singleton instance
bitrix_client = BitrixClient()
