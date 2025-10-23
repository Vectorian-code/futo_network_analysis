# data_generator.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class FUTODataGenerator:
    def __init__(self):
        self.networks = ["MTN", "Airtel", "Glo", "9mobile"]
        self.locations = [
            "Front Gate", "SENATE Building", "Library", "Round About", "Back Gate",
            "Hostel A", "Hostel B", "Hostel C", "Hostel D", "Hostel E",
            "NDDC", "TetFund", "PG Hostel", "Bj Services", "Student Affairs",
            "ICT", "Futo Cafe", "SEET", "SOSC extension", "Sops building",
            "SICT building", "Lecture Hall 2", "FUTO Medicals", "UCC Centre",
            "ACE fuels", "750 caps", "1000 Caps", "Futo Garden", "SOHT building", "Futo Park"
        ]

        # Define which network is best in which locations (MTN dominant, but others in specific areas)
        self.best_network_by_location = {
            # MTN Dominant Areas (16 locations - majority)
            "Front Gate": "MTN",
            "SENATE Building": "MTN",
            "Library": "MTN",
            "Round About": "MTN",
            "Student Affairs": "MTN",
            "UCC Centre": "MTN",
            "NDDC": "MTN",
            "TetFund": "MTN",
            "ICT": "MTN",
            "SICT building": "MTN",
            "Futo Park": "MTN",
            "Futo Garden": "MTN",
            "ACE fuels": "MTN",
            "FUTO Medicals": "MTN",
            "SOHT building": "MTN",
            "Sops building": "MTN",

            # Airtel Strong Areas - Hostels (6 locations)
            "Hostel A": "Airtel",
            "Hostel B": "Airtel",
            "Hostel C": "Airtel",
            "Hostel D": "Airtel",
            "Hostel E": "Airtel",
            "PG Hostel": "Airtel",

            # Glo Strong Areas (5 locations)
            "Back Gate": "Glo",
            "750 caps": "Glo",
            "1000 Caps": "Glo",
            "Bj Services": "Glo",
            "Futo Cafe": "Glo",

            # 9mobile Areas (3 locations - weakest)
            "Lecture Hall 2": "9mobile",
            "SEET": "9mobile",
            "SOSC extension": "9mobile"
        }

        # Network base profiles
        self.network_profiles = {
            "MTN": {"base_strength": -75, "reliability": 0.85, "speed_factor": 1.2},
            "Airtel": {"base_strength": -78, "reliability": 0.80, "speed_factor": 1.0},
            "Glo": {"base_strength": -82, "reliability": 0.65, "speed_factor": 0.8},
            "9mobile": {"base_strength": -85, "reliability": 0.55, "speed_factor": 0.7}
        }

        # Cost data
        self.cost_data = {
            "MTN": {"1GB": 300, "2GB": 500, "5GB": 1200, "10GB": 2000},
            "Airtel": {"1GB": 280, "2GB": 480, "5GB": 1150, "10GB": 1900},
            "Glo": {"1GB": 250, "2GB": 400, "5GB": 1000, "10GB": 1800},
            "9mobile": {"1GB": 270, "2GB": 450, "5GB": 1100, "10GB": 1850}
        }

        # Location-specific modifiers
        self.location_modifiers = {
            # Excellent signal areas
            "Front Gate": {"modifier": 8, "congestion": 0.1},
            "Round About": {"modifier": 10, "congestion": 0.2},
            "Futo Park": {"modifier": 12, "congestion": 0.1},
            "Futo Garden": {"modifier": 9, "congestion": 0.15},

            # Good signal areas
            "SENATE Building": {"modifier": 5, "congestion": 0.3},
            "Library": {"modifier": 4, "congestion": 0.4},
            "UCC Centre": {"modifier": 6, "congestion": 0.3},
            "Student Affairs": {"modifier": 5, "congestion": 0.35},

            # Moderate signal areas
            "ICT": {"modifier": 2, "congestion": 0.5},
            "SICT building": {"modifier": 3, "congestion": 0.45},
            "SEET": {"modifier": 1, "congestion": 0.6},
            "SOHT building": {"modifier": 2, "congestion": 0.5},
            "Sops building": {"modifier": 1, "congestion": 0.55},

            # Poor signal areas
            "Lecture Hall 2": {"modifier": -3, "congestion": 0.7},
            "FUTO Medicals": {"modifier": -2, "congestion": 0.6},
            "SOSC extension": {"modifier": -4, "congestion": 0.65},

            # Hostels (high congestion but Airtel optimized)
            "Hostel A": {"modifier": 3, "congestion": 0.8},  # Airtel strong here
            "Hostel B": {"modifier": 2, "congestion": 0.85},  # Airtel strong here
            "Hostel C": {"modifier": 3, "congestion": 0.8},  # Airtel strong here
            "Hostel D": {"modifier": 2, "congestion": 0.75},  # Airtel strong here
            "Hostel E": {"modifier": 3, "congestion": 0.8},  # Airtel strong here
            "PG Hostel": {"modifier": 4, "congestion": 0.7},  # Airtel strong here

            # Glo strong areas
            "Back Gate": {"modifier": 6, "congestion": 0.4},  # Glo strong
            "750 caps": {"modifier": 5, "congestion": 0.5},  # Glo strong
            "1000 Caps": {"modifier": 4, "congestion": 0.6},  # Glo strong
            "Bj Services": {"modifier": 5, "congestion": 0.55},  # Glo strong
            "Futo Cafe": {"modifier": 4, "congestion": 0.7},  # Glo strong

            # Other locations
            "NDDC": {"modifier": 1, "congestion": 0.6},
            "TetFund": {"modifier": 0, "congestion": 0.5},
            "ACE fuels": {"modifier": 2, "congestion": 0.4},
        }

    def is_best_network(self, network, location):
        """Check if this network is the best in this location"""
        return self.best_network_by_location.get(location) == network

    def generate_signal_strength(self, network, location):
        """Generate realistic signal strength in dBm"""
        base_profile = self.network_profiles[network]
        base_strength = base_profile["base_strength"]
        modifier = self.location_modifiers[location]["modifier"]

        # Boost signal for best network in location, reduce for others
        if self.is_best_network(network, location):
            strength_boost = 8  # Significant boost for best network
        else:
            strength_boost = -4  # Reduction for other networks

        # Add some randomness but keep it realistic
        variation = np.random.normal(0, 3)
        strength = base_strength + modifier + strength_boost + variation

        # Ensure realistic range
        return max(-120, min(-50, strength))

    def generate_signal_quality(self, network, location, signal_strength):
        """Generate signal quality score (0-100)"""
        base_quality = self.network_profiles[network]["reliability"] * 100
        congestion = self.location_modifiers[location]["congestion"]

        # Quality decreases with poor signal and high congestion
        signal_factor = max(0, (signal_strength + 120) / 70)  # Normalize to 0-1

        # Boost quality for best network
        if self.is_best_network(network, location):
            quality_boost = 15
        else:
            quality_boost = -8

        quality = base_quality * signal_factor * (1 - congestion * 0.3) + quality_boost

        # Add some variation
        variation = np.random.normal(0, 5)
        return max(0, min(100, quality + variation))

    def generate_sinr(self, network, location):
        """Generate SINR (Signal-to-Interference-plus-Noise Ratio)"""
        base_sinr = {
            "MTN": 20, "Airtel": 18, "Glo": 12, "9mobile": 10
        }[network]

        congestion = self.location_modifiers[location]["congestion"]

        # Boost SINR for best network
        if self.is_best_network(network, location):
            sinr_boost = 5
        else:
            sinr_boost = -3

        sinr = base_sinr - (congestion * 8) + sinr_boost + np.random.normal(0, 2)

        return max(0, min(30, sinr))

    def generate_data_speed(self, network, location, signal_strength):
        """Generate realistic data speeds in Mbps"""
        base_speed = {
            "MTN": 45, "Airtel": 40, "Glo": 25, "9mobile": 20
        }[network]

        # Speed reduces with poor signal
        signal_factor = max(0, (signal_strength + 100) / 50)
        congestion = self.location_modifiers[location]["congestion"]

        # Boost speed for best network
        if self.is_best_network(network, location):
            speed_boost = 12
        else:
            speed_boost = -6

        speed = base_speed * signal_factor * (1 - congestion * 0.4) + speed_boost
        speed += np.random.normal(0, 3)

        return max(0.1, min(100, speed))

    def generate_dataset(self, samples_per_location=15):
        """Generate complete dataset"""
        data = []

        for location in self.locations:
            for network in self.networks:
                for _ in range(samples_per_location):
                    signal_strength = self.generate_signal_strength(network, location)
                    signal_quality = self.generate_signal_quality(network, location, signal_strength)
                    sinr = self.generate_sinr(network, location)
                    data_speed = self.generate_data_speed(network, location, signal_strength)

                    data.append({
                        "location": location,
                        "network": network,
                        "signal_strength": round(signal_strength, 1),
                        "signal_quality": round(signal_quality, 1),
                        "sinr": round(sinr, 1),
                        "data_speed": round(data_speed, 1),
                        "timestamp": datetime.now() - timedelta(hours=np.random.randint(0, 168))
                    })

        return pd.DataFrame(data)

    def get_best_network_distribution(self):
        """Show distribution of best networks"""
        distribution = {}
        for network in self.networks:
            count = sum(1 for loc_net in self.best_network_by_location.values() if loc_net == network)
            distribution[network] = count
        return distribution


# Generate sample data
if __name__ == "__main__":
    generator = FUTODataGenerator()

    # Show best network distribution
    distribution = generator.get_best_network_distribution()
    print("BEST NETWORK DISTRIBUTION ACROSS 30 LOCATIONS:")
    print("=" * 50)
    for network, count in distribution.items():
        percentage = (count / 30) * 100
        print(f"{network}: {count} locations ({percentage:.1f}%)")

    print("\nDETAILED LOCATION BREAKDOWN:")
    print("=" * 50)
    for location, network in generator.best_network_by_location.items():
        print(f"{location}: {network}")

    # Generate dataset
    df = generator.generate_dataset(samples_per_location=15)
    print(f"\nGenerated {len(df)} records")

    # Save data
    df.to_csv("futo_network_data.csv", index=False)
    print("Data generation complete!")