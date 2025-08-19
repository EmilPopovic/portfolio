import logging
from fastapi import APIRouter
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
router = APIRouter(tags=['health'])

@router.get('/health')
async def health():
    return {
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'service': 'portfolio-api'
    }

@router.get('/health/ready')
async def readyness_check():
    return {'status': 'ready'}
