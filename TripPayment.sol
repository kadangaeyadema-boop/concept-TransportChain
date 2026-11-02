// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title TripPayment
 * @notice Smart contract pour la validation et le paiement des trajets
 *         sur la plateforme de transport décentralisée multimodale.
 * @dev Déploiement sur Ethereum Sepolia Testnet
 */
contract TripPayment {

    // ============================
    //  Structures de données
    // ============================

    struct Trip {
        uint256 tripId;           // Identifiant unique du trajet
        address payable user;     // Adresse Ethereum de l'utilisateur
        uint256 amount;           // Montant payé en wei
        bool isPaid;              // Paiement effectué
        bool isValidated;         // Trajet validé par l'opérateur
        uint256 timestamp;        // Horodatage du paiement
        string metadata;          // Métadonnées JSON (départ, arrivée, mode)
    }

    // ============================
    //  Variables d'état
    // ============================

    address public owner;                          // Propriétaire du contrat (opérateur)
    mapping(uint256 => Trip) public trips;         // Mapping tripId → Trip
    mapping(address => uint256[]) public userTrips; // Historique par utilisateur
    uint256 public totalTrips;                     // Compteur de trajets
    uint256 public totalRevenue;                   // Revenus cumulés

    // ============================
    //  Événements
    // ============================

    event PaymentReceived(
        uint256 indexed tripId,
        address indexed user,
        uint256 amount,
        uint256 timestamp
    );

    event TripValidated(
        uint256 indexed tripId,
        address indexed validator,
        uint256 timestamp
    );

    event Refunded(
        uint256 indexed tripId,
        address indexed user,
        uint256 amount
    );

    // ============================
    //  Modificateurs
    // ============================

    modifier onlyOwner() {
        require(msg.sender == owner, "Acces reserve a l'operateur");
        _;
    }

    modifier tripExists(uint256 tripId) {
        require(trips[tripId].user != address(0), "Trajet introuvable");
        _;
    }

    // ============================
    //  Constructeur
    // ============================

    constructor() {
        owner = msg.sender;
        totalTrips = 0;
        totalRevenue = 0;
    }

    // ============================
    //  Fonctions principales
    // ============================

    /**
     * @notice Enregistre le paiement d'un trajet
     * @param tripId Identifiant unique du trajet
     * @param metadata JSON contenant les détails (départ, arrivée, mode, durée)
     */
    function payTrip(uint256 tripId, string calldata metadata) external payable {
        require(msg.value > 0, "Le montant doit etre superieur a 0");
        require(trips[tripId].user == address(0), "Trajet deja enregistre");

        trips[tripId] = Trip({
            tripId: tripId,
            user: payable(msg.sender),
            amount: msg.value,
            isPaid: true,
            isValidated: false,
            timestamp: block.timestamp,
            metadata: metadata
        });

        userTrips[msg.sender].push(tripId);
        totalTrips++;
        totalRevenue += msg.value;

        emit PaymentReceived(tripId, msg.sender, msg.value, block.timestamp);
    }

    /**
     * @notice Valide un trajet effectué (appelé par l'opérateur)
     * @param tripId Identifiant du trajet à valider
     */
    function validateTrip(uint256 tripId)
        external
        onlyOwner
        tripExists(tripId)
    {
        require(trips[tripId].isPaid, "Trajet non paye");
        require(!trips[tripId].isValidated, "Trajet deja valide");

        trips[tripId].isValidated = true;

        emit TripValidated(tripId, msg.sender, block.timestamp);
    }

    /**
     * @notice Rembourse un trajet non validé
     * @param tripId Identifiant du trajet à rembourser
     */
    function refundTrip(uint256 tripId)
        external
        onlyOwner
        tripExists(tripId)
    {
        Trip storage trip = trips[tripId];
        require(trip.isPaid, "Trajet non paye");
        require(!trip.isValidated, "Trajet deja valide, remboursement impossible");

        uint256 refundAmount = trip.amount;
        trip.isPaid = false;
        trip.amount = 0;
        totalRevenue -= refundAmount;

        trip.user.transfer(refundAmount);

        emit Refunded(tripId, trip.user, refundAmount);
    }

    // ============================
    //  Fonctions de lecture
    // ============================

    /**
     * @notice Retourne les détails d'un trajet
     */
    function getTrip(uint256 tripId)
        external
        view
        tripExists(tripId)
        returns (Trip memory)
    {
        return trips[tripId];
    }

    /**
     * @notice Retourne le statut de paiement d'un trajet
     */
    function getTripStatus(uint256 tripId)
        external
        view
        returns (bool isPaid, bool isValidated)
    {
        Trip memory trip = trips[tripId];
        return (trip.isPaid, trip.isValidated);
    }

    /**
     * @notice Retourne les IDs de trajets d'un utilisateur
     */
    function getUserTrips(address user)
        external
        view
        returns (uint256[] memory)
    {
        return userTrips[user];
    }

    /**
     * @notice Retourne les statistiques du contrat
     */
    function getStats()
        external
        view
        returns (uint256 nbTrips, uint256 revenue, address contractOwner)
    {
        return (totalTrips, totalRevenue, owner);
    }

    /**
     * @notice Retire les fonds accumulés (opérateur seulement)
     */
    function withdraw() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "Solde vide");
        payable(owner).transfer(balance);
    }

    /**
     * @notice Transfert de propriété du contrat
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Adresse invalide");
        owner = newOwner;
    }
}
