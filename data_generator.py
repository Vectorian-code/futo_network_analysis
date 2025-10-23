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

        # Base performance profiles for each network
        self.network_profiles = {
            "MTN": {"base_strength": -75, "reliability": 0.85, "speed_factor": 1.2},
            "Airtel": {"base_strength": -78, "reliability": 0.80, "speed_factor": 1.0},
            "Glo": {"base_strength": -82, "reliability": 0.65, "speed_factor": 0.8},
            "9mobile": {"base_strength": -85, "reliability": 0.55, "speed_factor": 0.7}
        }

        # NEW: Cost data for cost-benefit analysis
        self.cost_data = {
            "MTN": {"1GB": 300, "2GB": 500, "5GB": 1200, "10GB": 2000},
            "Airtel": {"1GB": 280, "2GB": 480, "5GB": 1150, "10GB": 1900},
            "Glo": {"1GB": 250, "2GB": 400, "5GB": 1000, "10GB": 1800},
            "9mobile": {"1GB": 270, "2GB": 450, "5GB": 1100, "10GB": 1850}
        }

        # NEW: Time-based performance patterns
        self.time_patterns = {
            "morning": {"congestion": 0.3, "performance": 1.0},
            "afternoon": {"congestion": 0.7, "performance": 0.8},
            "evening": {"congestion": 0.9, "performance": 0.6},
            "night": {"congestion": 0.4, "performance": 1.1}
        }

        # Location-specific modifiers (realistic FUTO conditions)
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

            # Poor signal areas (buildings with concrete/many walls)
            "Lecture Hall 2": {"modifier": -3, "congestion": 0.7},
            "FUTO Medicals": {"modifier": -2, "congestion": 0.6},
            "SOSC extension": {"modifier": -4, "congestion": 0.65},

            # Hostels (high congestion)
            "Hostel A": {"modifier": -1, "congestion": 0.8},
            "Hostel B": {"modifier": -2, "congestion": 0.85},
            "Hostel C": {"modifier": -3, "congestion": 0.8},
            "Hostel D": {"modifier": -1, "congestion": 0.75},
            "Hostel E": {"modifier": -2, "congestion": 0.8},
            "PG Hostel": {"modifier": 0, "congestion": 0.7},

            # Other locations
            "Back Gate": {"modifier": 4, "congestion": 0.4},
            "NDDC": {"modifier": 1, "congestion": 0.6},
            "TetFund": {"modifier": 0, "congestion": 0.5},
            "Bj Services": {"modifier": -1, "congestion": 0.55},
            "Futo Cafe": {"modifier": 3, "congestion": 0.7},
            "ACE fuels": {"modifier": 2, "congestion": 0.4},
            "750 caps": {"modifier": 1, "congestion": 0.5},
            "1000 Caps": {"modifier": 0, "congestion": 0.6}
        }

    def generate_signal_strength(self, network, location, time_of_day="afternoon"):
        """Generate realistic signal strength in dBm"""
        base = self.network_profiles[network]["base_strength"]
        modifier = self.location_modifiers[location]["modifier"]
        time_factor = self.time_patterns[time_of_day]["performance"]

        # Add some randomness but keep it realistic
        variation = np.random.normal(0, 3)
        strength = base + modifier + variation

        # Apply time-based variation
        strength *= time_factor

        # Ensure realistic range
        return max(-120, min(-50, strength))

    def generate_signal_quality(self, network, location, signal_strength, time_of_day="afternoon"):
        """Generate signal quality score (0-100)"""
        base_quality = self.network_profiles[network]["reliability"] * 100
        congestion = self.location_modifiers[location]["congestion"]
        time_congestion = self.time_patterns[time_of_day]["congestion"]

        # Combined congestion effect
        total_congestion = min(0.95, congestion + time_congestion * 0.5)

        # Quality decreases with poor signal and high congestion
        signal_factor = max(0, (signal_strength + 120) / 70)  # Normalize to 0-1
        quality = base_quality * signal_factor * (1 - total_congestion * 0.3)

        # Add some variation
        variation = np.random.normal(0, 5)
        return max(0, min(100, quality + variation))

    def generate_sinr(self, network, location, time_of_day="afternoon"):
        """Generate SINR (Signal-to-Interference-plus-Noise Ratio)"""
        base_sinr = {
            "MTN": 20, "Airtel": 18, "Glo": 12, "9mobile": 10
        }[network]

        congestion = self.location_modifiers[location]["congestion"]
        time_congestion = self.time_patterns[time_of_day]["congestion"]
        total_congestion = min(0.95, congestion + time_congestion * 0.5)

        sinr = base_sinr - (total_congestion * 8) + np.random.normal(0, 2)

        return max(0, min(30, sinr))

    def generate_data_speed(self, network, location, signal_strength, time_of_day="afternoon"):
        """Generate realistic data speeds in Mbps"""
        base_speed = {
            "MTN": 45, "Airtel": 40, "Glo": 25, "9mobile": 20
        }[network]

        # Speed reduces with poor signal
        signal_factor = max(0, (signal_strength + 100) / 50)
        congestion = self.location_modifiers[location]["congestion"]
        time_congestion = self.time_patterns[time_of_day]["congestion"]
        total_congestion = min(0.95, congestion + time_congestion * 0.5)

        time_factor = self.time_patterns[time_of_day]["performance"]

        speed = base_speed * signal_factor * (1 - total_congestion * 0.4) * time_factor
        speed += np.random.normal(0, 3)

        return max(0.1, min(100, speed))

    def generate_time_based_dataset(self):
        """NEW: Generate dataset with time-based variations"""
        data = []
        times_of_day = ["morning", "afternoon", "evening", "night"]

        for location in self.locations:
            for network in self.networks:
                for time_of_day in times_of_day:
                    for _ in range(5):  # 5 samples per time period
                        signal_strength = self.generate_signal_strength(network, location, time_of_day)
                        signal_quality = self.generate_signal_quality(network, location, signal_strength, time_of_day)
                        sinr = self.generate_sinr(network, location, time_of_day)
                        data_speed = self.generate_data_speed(network, location, signal_strength, time_of_day)

                        # Create timestamp based on time of day
                        hour_map = {"morning": 8, "afternoon": 14, "evening": 20, "night": 2}

                        data.append({
                            "location": location,
                            "network": network,
                            "signal_strength": round(signal_strength, 1),
                            "signal_quality": round(signal_quality, 1),
                            "sinr": round(sinr, 1),
                            "data_speed": round(data_speed, 1),
                            "time_of_day": time_of_day,
                            "timestamp": datetime.now().replace(hour=hour_map[time_of_day], minute=0,
                                                                second=0) - timedelta(days=np.random.randint(0, 7))
                        })

        return pd.DataFrame(data)

    def generate_dataset(self, samples_per_location=10):
        """Generate complete dataset (original method for compatibility)"""
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

    def get_cost_data(self):
        """NEW: Get cost data for analysis"""
        return self.cost_data

    def get_user_experience_data(self):
        """NEW: Generate simulated user experience data"""
        user_experience = {}

        for network in self.networks:
            network_data = self.generate_dataset()
            net_data = network_data[network_data['network'] == network]

            # Calculate user experience metrics
            avg_quality = net_data['signal_quality'].mean()
            avg_speed = net_data['data_speed'].mean()
            reliability = (net_data['signal_quality'] > 70).mean()

            # Convert to star ratings (1-5)
            call_quality_stars = min(5, max(1, round(avg_quality / 20)))
            speed_stars = min(5, max(1, round(avg_speed / 10)))
            reliability_stars = min(5, max(1, round(reliability * 5)))

            user_experience[network] = {
                'call_quality': call_quality_stars,
                'data_speed': speed_stars,
                'reliability': reliability_stars,
                'overall': (call_quality_stars + speed_stars + reliability_stars) / 3
            }

        return user_experience


# Generate sample data
if __name__ == "__main__":
    generator = FUTODataGenerator()

    # Generate main dataset
    df = generator.generate_dataset(samples_per_location=15)
    print(f"Generated {len(df)} main records")

    # Generate time-based dataset for time analysis
    time_df = generator.generate_time_based_dataset()
    print(f"Generated {len(time_df)} time-based records")

    # Save both datasets
    df.to_csv("futo_network_data.csv", index=False)
    time_df.to_csv("futo_network_time_data.csv", index=False)

    print("Data generation complete!")
    print(df.head())