"""
Semaine 3 - Module Blockchain simulée en Python
SHA-256, blocs chaînés, validation de la chaîne
Plateforme de transport décentralisée
"""

import hashlib
import json
import time
import uuid


class Transaction:
    """Représente une transaction de paiement de trajet."""

    def __init__(self, from_address, to_address, montant, trajet_id, details=None):
        self.tx_id = str(uuid.uuid4()).replace('-', '')[:16]
        self.from_address = from_address
        self.to_address = to_address
        self.montant = round(montant, 4)
        self.trajet_id = trajet_id
        self.details = details or {}
        self.timestamp = time.time()

    def to_dict(self):
        return {
            'tx_id': self.tx_id,
            'from': self.from_address,
            'to': self.to_address,
            'montant': self.montant,
            'trajet_id': self.trajet_id,
            'details': self.details,
            'timestamp': self.timestamp
        }

    def __repr__(self):
        return f"TX({self.tx_id[:8]}... | {self.from_address[:6]}→{self.to_address[:6]} | ${self.montant})"


class Block:
    """Un bloc dans la blockchain."""

    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Calcule le hash SHA-256 du bloc."""
        block_str = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [t.to_dict() for t in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_str.encode()).hexdigest()

    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [t.to_dict() for t in self.transactions],
            'previous_hash': self.previous_hash,
            'hash': self.hash,
            'nonce': self.nonce,
            'nb_transactions': len(self.transactions)
        }

    def __repr__(self):
        return f"Block(#{self.index} | {len(self.transactions)} tx | hash:{self.hash[:12]}...)"


class Blockchain:
    """Chaîne de blocs pour la plateforme de transport."""

    OPERATOR_ADDRESS = "0xOPERATOR000000000000000000000000000000"

    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        """Crée le bloc genesis (premier bloc de la chaîne)."""
        genesis = Block(
            index=0,
            transactions=[],
            previous_hash='0' * 64
        )
        self.chain.append(genesis)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        """Ajoute une transaction au pool en attente."""
        self.pending_transactions.append(transaction)
        return transaction.tx_id

    def mine_block(self):
        """
        Crée un nouveau bloc avec les transactions en attente.
        Retourne le bloc miné ou None s'il n'y a rien à miner.
        """
        if not self.pending_transactions:
            return None

        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions.copy(),
            previous_hash=self.last_block.hash
        )
        self.chain.append(new_block)
        self.pending_transactions = []
        return new_block

    def pay_trip(self, user_address, montant, trajet_id, details=None):
        """
        Enregistre le paiement d'un trajet sur la blockchain.
        Crée une transaction et la mine immédiatement.
        Retourne le hash de transaction.
        """
        tx = Transaction(
            from_address=user_address,
            to_address=self.OPERATOR_ADDRESS,
            montant=montant,
            trajet_id=trajet_id,
            details=details or {}
        )
        tx_id = self.add_transaction(tx)
        block = self.mine_block()
        return {
            'tx_id': tx_id,
            'block_hash': block.hash,
            'block_index': block.index,
            'timestamp': tx.timestamp,
            'status': 'confirmed'
        }

    def is_valid(self):
        """
        Vérifie l'intégrité de toute la chaîne.
        Retourne (True, []) si valide, (False, [erreurs]) sinon.
        """
        errors = []
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Vérification du hash du bloc courant
            recalculated = current.calculate_hash()
            if current.hash != recalculated:
                errors.append(f"Bloc #{i}: hash invalide")

            # Vérification du chaînage
            if current.previous_hash != previous.hash:
                errors.append(f"Bloc #{i}: chaînage rompu avec le bloc #{i-1}")

        return (len(errors) == 0, errors)

    def get_transaction(self, tx_id):
        """Recherche une transaction par son ID dans toute la chaîne."""
        for block in self.chain:
            for tx in block.transactions:
                if tx.tx_id == tx_id:
                    return {'transaction': tx.to_dict(), 'block_index': block.index, 'block_hash': block.hash}
        return None

    def get_user_history(self, user_address):
        """Retourne l'historique des transactions d'un utilisateur."""
        history = []
        for block in self.chain:
            for tx in block.transactions:
                if tx.from_address == user_address:
                    history.append({**tx.to_dict(), 'block_index': block.index})
        return sorted(history, key=lambda x: x['timestamp'], reverse=True)

    def get_stats(self):
        """Statistiques de la blockchain."""
        total_tx = sum(len(b.transactions) for b in self.chain)
        return {
            'nb_blocs': len(self.chain),
            'nb_transactions': total_tx,
            'pending': len(self.pending_transactions),
            'dernier_hash': self.last_block.hash[:16] + '...'
        }

    def to_dict(self):
        return {
            'chain': [b.to_dict() for b in self.chain],
            'length': len(self.chain),
            'stats': self.get_stats()
        }

    def __repr__(self):
        valid, _ = self.is_valid()
        return f"Blockchain({len(self.chain)} blocs | valide:{valid})"


# Instance globale (simulant un nœud blockchain)
_blockchain_instance = None

def get_blockchain():
    global _blockchain_instance
    if _blockchain_instance is None:
        _blockchain_instance = Blockchain()
    return _blockchain_instance


if __name__ == '__main__':
    print("=== Test de la Blockchain ===\n")
    bc = Blockchain()

    # Test : paiement de 3 trajets
    result1 = bc.pay_trip("0xUSER_ALICE_001", 2.50, 101, {'depart': 'Gare Centrale', 'arrivee': 'Université Nord'})
    print(f"Trajet 1 payé | TX: {result1['tx_id']} | Bloc #{result1['block_index']}")

    result2 = bc.pay_trip("0xUSER_BOB_002", 0.80, 102, {'depart': 'Quartier Est', 'arrivee': 'Centre Commercial Ouest'})
    print(f"Trajet 2 payé | TX: {result2['tx_id']} | Bloc #{result2['block_index']}")

    result3 = bc.pay_trip("0xUSER_ALICE_001", 1.60, 103, {'depart': 'Place des Arts', 'arrivee': 'Parc Lafontaine'})
    print(f"Trajet 3 payé | TX: {result3['tx_id']} | Bloc #{result3['block_index']}")

    print(f"\nChaîne : {bc}")
    valid, errors = bc.is_valid()
    print(f"Validation : {'✅ Valide' if valid else '❌ Invalide'}")
    if errors:
        for e in errors:
            print(f"  Erreur: {e}")

    print(f"\nHistorique Alice:")
    for tx in bc.get_user_history("0xUSER_ALICE_001"):
        print(f"  TX {tx['tx_id']} | ${tx['montant']} | Trajet #{tx['trajet_id']}")

    stats = bc.get_stats()
    print(f"\nStats: {stats['nb_blocs']} blocs, {stats['nb_transactions']} transactions")
