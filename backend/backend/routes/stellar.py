from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from stellar_service import StellarTransaction

router = APIRouter()

# Modelo para a requisição de transação
class TransactionRequest(BaseModel):
    amount: float | None = None
    recipient: str | None = None

@router.post("/stellar/")
async def create_transaction(transaction: TransactionRequest | None = None):
    stellar = StellarTransaction()
    
    # Se recebeu dados de transação, usa eles
    amount = transaction.amount if transaction else None
    recipient = transaction.recipient if transaction else None
    
    result = stellar.create_and_send_transaction(
        amount=amount,
        recipient=recipient
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.get("/stellar/{tx_hash}")
async def get_transaction(tx_hash: str):
    stellar = StellarTransaction()
    result = stellar.verify_transaction(tx_hash)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result