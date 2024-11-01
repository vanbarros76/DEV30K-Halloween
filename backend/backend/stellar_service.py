from stellar_sdk import Server, Keypair, Network, TransactionBuilder, Asset
import base64
from dotenv import load_dotenv
import os

load_dotenv()

class StellarTransaction:
    def __init__(self):
        try:
            self.server = Server("https://horizon-testnet.stellar.org")  # Usando Testnet
            self.network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE
            
            self.secret_key = os.getenv("STELLAR_SECRET_KEY")
            if not self.secret_key:
                raise ValueError("STELLAR_SECRET_KEY não encontrada no arquivo .env")
                
            self.keypair = Keypair.from_secret(self.secret_key)
            
            # Debug info
            print("\n=== Debug Info ===")
            print(f"Chave pública: {self.keypair.public_key}")
            print(f"Rede: Testnet")
            
            # Verificar saldo
            account = self.server.accounts().account_id(self.keypair.public_key).call()
            for balance in account['balances']:
                if balance['asset_type'] == 'native':
                    print(f"Saldo XLM: {balance['balance']}")
            print("================\n")
        except Exception as e:
            print(f"Erro na inicialização: {str(e)}")
            raise

    def sign_message(self, message="DEV30K"):
        """Assina a mensagem usando a chave privada"""
        try:
            print(f"\nAssinando mensagem: '{message}'")
            message_bytes = message.encode()
            signature = self.keypair.sign(message_bytes)
            encoded_signature = base64.b64encode(signature).decode()
            print(f"Assinatura gerada: {encoded_signature}")
            return encoded_signature
        except Exception as e:
            print(f"Erro ao assinar mensagem: {str(e)}")
            raise

    def create_and_send_transaction(self, amount=None, recipient=None):
        try:
            # Verificar saldo primeiro
            account = self.server.accounts().account_id(self.keypair.public_key).call()
            current_balance = 0
            for balance in account['balances']:
                if balance['asset_type'] == 'native':
                    current_balance = float(balance['balance'])
                    print(f"\nSaldo atual: {current_balance} XLM")
                    break

            # Verificar se tem saldo suficiente
            if amount is not None:
                required_balance = float(amount) + 0.00001  # taxa de transação
                if current_balance < required_balance:
                    return {
                        "status": "error",
                        "message": f"Saldo insuficiente. Necessário: {required_balance} XLM, Atual: {current_balance} XLM"
                    }

            # 1. Assinar "DEV30K"
            signature = self.sign_message("DEV30K")
            print(f"\n1. Mensagem 'DEV30K' assinada")
            
            # 2. Criar e enviar transação
            source_account = self.server.load_account(self.keypair.public_key)
            
            # Pegar apenas os primeiros 64 caracteres da assinatura
            truncated_signature = signature[:64]
            
            # Criar o builder da transação
            builder = TransactionBuilder(
                source_account=source_account,
                network_passphrase=self.network_passphrase,
                base_fee=self.server.fetch_base_fee()
            )

            # Adicionar memo e assinatura
            builder.add_text_memo("DEV30K")
            builder.append_manage_data_op(
                data_name="signature",
                data_value=truncated_signature,
                source=self.keypair.public_key
            )

            # Se tiver valor e destinatário, adiciona o pagamento
            if amount is not None and recipient is not None:
                print(f"\nAdicionando pagamento: {amount} XLM para {recipient}")
                builder.append_payment_op(
                    destination=recipient,
                    amount=str(amount),
                    asset=Asset.native()  # XLM
                )

            # Construir e enviar a transação
            transaction = builder.set_timeout(30).build()
            transaction.sign(self.keypair)
            
            print("\nEnviando transação...")
            response = self.server.submit_transaction(transaction)
            
            print(f"\n2. Transação enviada!")
            print(f"Hash: {response['hash']}")
            print(f"Assinatura completa: {signature}")
            print(f"Assinatura truncada: {truncated_signature}")
            
            result = {
                "status": "success",
                "hash": response["hash"],
                "signature": signature,
                "truncated_signature": truncated_signature,
                "message": "DEV30K"
            }

            # Adicionar informações de pagamento se houver
            if amount is not None and recipient is not None:
                result.update({
                    "amount": amount,
                    "recipient": recipient
                })
            
            return result

        except Exception as e:
            print(f"\nErro na transação: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    def verify_transaction(self, transaction_hash):
        """Verifica uma transação pelo hash"""
        try:
            print(f"\nVerificando transação: {transaction_hash}")
            transaction = self.server.transactions().transaction(transaction_hash).call()
            print("Transação encontrada!")
            return {
                "status": "success",
                "transaction": transaction
            }
        except Exception as e:
            print(f"Erro ao verificar transação: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }


# Exemplo de uso
if __name__ == "__main__":
    stellar = StellarTransaction()
    
    # Criar e enviar a transação
    result = stellar.create_and_send_transaction()
    
    if result["status"] == "success":
        print(f"Transação enviada com sucesso!")
        print(f"Hash da transação: {result['hash']}")
        print(f"Assinatura: {result['signature']}")
        
        # Verificar a transação
        verification = stellar.verify_transaction(result["hash"])
        if verification["status"] == "success":
            print("Transação verificada com sucesso!")
    else:
        print(f"Erro: {result['message']}")