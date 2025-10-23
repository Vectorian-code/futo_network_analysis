# enhanced_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import folium
from streamlit_folium import st_folium


class EnhancedFUTODashboard:
    def __init__(self):
        self.generator = FUTODataGenerator()
        self.df = self.load_data()
        self.setup_coordinates()

    def setup_coordinates(self):
        """Set up approximate coordinates for FUTO locations"""
        self.location_coordinates = {
            "Front Gate": {"lat": 5.4063, "lon": 7.0713},
            "SENATE Building": {"lat": 5.4070, "lon": 7.0720},
            "Library": {"lat": 5.4075, "lon": 7.0710},
            "Round About": {"lat": 5.4072, "lon": 7.0715},
            "Back Gate": {"lat": 5.4080, "lon": 7.0705},
            "Hostel A": {"lat": 5.4060, "lon": 7.0730},
            "Hostel B": {"lat": 5.4062, "lon": 7.0735},
            "Hostel C": {"lat": 5.4065, "lon": 7.0740},
            "Hostel D": {"lat": 5.4068, "lon": 7.0745},
            "Hostel E": {"lat": 5.4070, "lon": 7.0750},
            "NDDC": {"lat": 5.4078, "lon": 7.0725},
            "TetFund": {"lat": 5.4076, "lon": 7.0728},
            "PG Hostel": {"lat": 5.4058, "lon": 7.0748},
            "Bj Services": {"lat": 5.4073, "lon": 7.0718},
            "Student Affairs": {"lat": 5.4074, "lon": 7.0722},
            "ICT": {"lat": 5.4077, "lon": 7.0712},
            "Futo Cafe": {"lat": 5.4071, "lon": 7.0717},
            "SEET": {"lat": 5.4079, "lon": 7.0719},
            "SOSC extension": {"lat": 5.4081, "lon": 7.0721},
            "Sops building": {"lat": 5.4082, "lon": 7.0723},
            "SICT building": {"lat": 5.4083, "lon": 7.0720},
            "Lecture Hall 2": {"lat": 5.4072, "lon": 7.0726},
            "FUTO Medicals": {"lat": 5.4067, "lon": 7.0724},
            "UCC Centre": {"lat": 5.4069, "lon": 7.0728},
            "ACE fuels": {"lat": 5.4064, "lon": 7.0716},
            "750 caps": {"lat": 5.4059, "lon": 7.0740},
            "1000 Caps": {"lat": 5.4057, "lon": 7.0742},
            "Futo Garden": {"lat": 5.4075, "lon": 7.0708},
            "SOHT building": {"lat": 5.4080, "lon": 7.0718},
            "Futo Park": {"lat": 5.4078, "lon": 7.0705}
        }

    def load_data(self):
        """Load or generate data"""
        try:
            df = pd.read_csv("futo_network_data.csv")
        except:
            st.info("Generating realistic FUTO network data...")
            df = self.generator.generate_dataset(samples_per_location=15)
            df.to_csv("futo_network_data.csv", index=False)
        return df

    def create_campus_overview_map(self):
        """NEW: Create campus overview map showing all locations"""
        st.subheader("🗺️ FUTO Campus Overview")

        # Create a simple map showing all locations
        map_data = []
        for location, coords in self.location_coordinates.items():
            map_data.append({
                'lat': coords['lat'],
                'lon': coords['lon'],
                'location': location,
                'color': 'blue'
            })

        map_df = pd.DataFrame(map_data)

        if not map_df.empty:
            fig = px.scatter_mapbox(
                map_df,
                lat='lat',
                lon='lon',
                hover_name='location',
                hover_data={'lat': False, 'lon': False},
                color_discrete_sequence=['blue'],
                size_max=15,
                zoom=15,
                height=400,
                title="FUTO Campus - All 30 Locations"
            )

            fig.update_layout(
                mapbox_style="open-street-map",
                mapbox=dict(
                    center=dict(lat=5.4074, lon=7.0716),
                    zoom=15
                ),
                margin={"r": 0, "t": 50, "l": 0, "b": 0},
                showlegend=False
            )

            # Add custom hover template
            fig.update_traces(
                hovertemplate=(
                    "<b>%{hovertext}</b>"
                    "<extra></extra>"
                ),
                marker=dict(size=12)
            )

            st.plotly_chart(fig, use_container_width=True)

    def create_overview_metrics(self):
        """Display overview metrics with performance table for ALL locations"""
        st.markdown('<div class="main-header">📶 FUTO Mobile Network Analysis Dashboard</div>', unsafe_allow_html=True)

        # NEW: Add campus overview map at the top
        self.create_campus_overview_map()

        metrics = self.calculate_metrics()
        best_networks = self.get_best_network_per_location()

        col1, col2, col3, col4 = st.columns(4)

        # Find overall best and worst networks
        overall_scores = {}
        for network, metric in metrics.items():
            overall_scores[network] = (metric['avg_signal_quality'] + metric['avg_data_speed']) / 2

        best_network = max(overall_scores, key=overall_scores.get)
        worst_network = min(overall_scores, key=overall_scores.get)

        for network in self.generator.networks:
            metric_data = metrics[network]
            with col1 if network == "MTN" else col2 if network == "Airtel" else col3 if network == "Glo" else col4:
                css_class = "metric-card best-network" if network == best_network else "metric-card worst-network" if network == worst_network else "metric-card"
                st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                st.metric(
                    label=f"{network}",
                    value=f"{metric_data['avg_signal_quality']:.1f}%",
                    delta=f"{metric_data['avg_data_speed']:.1f} Mbps"
                )
                st.caption(f"Signal: {metric_data['avg_signal_strength']:.1f} dBm")
                st.markdown('</div>', unsafe_allow_html=True)

        # NEW: Network Performance Summary Table for ALL 30 Locations
        st.subheader("📋 Network Performance Across All 30 Campus Locations")

        # Create performance table for ALL locations
        performance_data = []
        for location in self.generator.locations:  # Use ALL locations
            location_data = self.df[self.df['location'] == location]
            location_performance = {}

            for network in self.generator.networks:
                network_data = location_data[location_data['network'] == network]
                if len(network_data) > 0:
                    avg_quality = network_data['signal_quality'].mean()
                    avg_speed = network_data['data_speed'].mean()

                    # Create performance indicator
                    if avg_quality > 80:
                        indicator = "🟢"
                        level = "Excellent"
                    elif avg_quality > 60:
                        indicator = "🟡"
                        level = "Good"
                    elif avg_quality > 40:
                        indicator = "🟠"
                        level = "Fair"
                    else:
                        indicator = "🔴"
                        level = "Poor"

                    location_performance[network] = {
                        'quality': f"{avg_quality:.1f}%",
                        'speed': f"{avg_speed:.1f} Mbps",
                        'indicator': indicator,
                        'level': level
                    }
                else:
                    location_performance[network] = {
                        'quality': "N/A",
                        'speed': "N/A",
                        'indicator': "⚫",
                        'level': "No Data"
                    }

            # Find best network for this location
            best_net = best_networks.get(location, "Unknown")

            performance_data.append({
                'Location': location,
                'Best Network': best_net,
                'MTN': location_performance['MTN'],
                'Airtel': location_performance['Airtel'],
                'Glo': location_performance['Glo'],
                '9mobile': location_performance['9mobile']
            })

        # Display ALL locations in a scrollable table
        st.write("#### 📊 Detailed Performance Table")

        # Create a DataFrame for the table view
        table_data = []
        for location_data in performance_data:
            table_data.append({
                'Location': location_data['Location'],
                'Best Network': location_data['Best Network'],
                'MTN Quality': location_data['MTN']['quality'],
                'MTN Speed': location_data['MTN']['speed'],
                'MTN Level': location_data['MTN']['level'],
                'Airtel Quality': location_data['Airtel']['quality'],
                'Airtel Speed': location_data['Airtel']['speed'],
                'Airtel Level': location_data['Airtel']['level'],
                'Glo Quality': location_data['Glo']['quality'],
                'Glo Speed': location_data['Glo']['speed'],
                'Glo Level': location_data['Glo']['level'],
                '9mobile Quality': location_data['9mobile']['quality'],
                '9mobile Speed': location_data['9mobile']['speed'],
                '9mobile Level': location_data['9mobile']['level']
            })

        table_df = pd.DataFrame(table_data)

        # Display the full table
        st.dataframe(
            table_df,
            use_container_width=True,
            height=600  # Scrollable height
        )

        # Also show expandable sections for detailed view
        st.write("#### 🔍 Detailed Location Analysis")

        # Group locations by area type for better organization
        area_groups = {
            "🏛️ Academic & Administrative": [
                "SENATE Building", "Library", "ICT", "SICT building", "SEET",
                "SOHT building", "Sops building", "Lecture Hall 2", "Student Affairs",
                "UCC Centre", "NDDC", "TetFund"
            ],
            "🏠 Hostels & Accommodation": [
                "Hostel A", "Hostel B", "Hostel C", "Hostel D", "Hostel E",
                "PG Hostel", "750 caps", "1000 Caps", "Bj Services"
            ],
            "🎯 Social & Commercial Areas": [
                "Front Gate", "Back Gate", "Round About", "Futo Cafe", "Futo Park",
                "Futo Garden", "ACE fuels", "FUTO Medicals"
            ]
        }

        for area_name, area_locations in area_groups.items():
            with st.expander(f"{area_name} ({len(area_locations)} locations)", expanded=False):
                for location in area_locations:
                    location_data = next((item for item in performance_data if item['Location'] == location), None)
                    if location_data:
                        cols = st.columns(5)
                        with cols[0]:
                            st.write(f"**{location}**")
                            st.caption(f"Best: {location_data['Best Network']}")

                        networks = ['MTN', 'Airtel', 'Glo', '9mobile']
                        for idx, network in enumerate(networks):
                            with cols[idx + 1]:
                                perf = location_data[network]
                                st.metric(
                                    label=f"{network}",
                                    value=f"{perf['indicator']} {perf['quality']}",
                                    delta=perf['speed']
                                )
                                st.caption(perf['level'])
                        st.markdown("---")

        # Quick insights
        st.info("""
        💡 **Quick Insights**: 
        - **🟢 Excellent** (>80% quality), **🟡 Good** (60-80%), **🟠 Fair** (40-60%), **🔴 Poor** (<40%)
        - Table shows all 30 FUTO campus locations with detailed network performance
        - Use the expandable sections for area-wise analysis
        """)

    def calculate_metrics(self):
        """Calculate overall metrics"""
        metrics = {}
        for network in self.generator.networks:
            network_data = self.df[self.df['network'] == network]
            metrics[network] = {
                'avg_signal_strength': network_data['signal_strength'].mean(),
                'avg_signal_quality': network_data['signal_quality'].mean(),
                'avg_data_speed': network_data['data_speed'].mean(),
                'reliability_score': (network_data['signal_quality'] > 70).mean() * 100
            }
        return metrics

    def get_best_network_per_location(self):
        """Determine best network for each location"""
        best_networks = {}
        for location in self.generator.locations:
            location_data = self.df[self.df['location'] == location]
            scores = {}
            for network in self.generator.networks:
                net_data = location_data[location_data['network'] == network]
                if len(net_data) > 0:
                    # Composite score considering all metrics
                    score = (net_data['signal_quality'].mean() * 0.3 +
                             (100 - abs(net_data['signal_strength'].mean() + 80)) * 0.3 +
                             net_data['data_speed'].mean() * 0.4)
                    scores[network] = score
            if scores:
                best_networks[location] = max(scores, key=scores.get)
        return best_networks

    def create_network_comparison_charts(self):
        """Create comparison charts"""
        st.subheader("📊 Network Performance Comparison")

        tab1, tab2, tab3, tab4 = st.tabs(["Signal Strength", "Signal Quality", "Data Speed", "SINR"])

        with tab1:
            fig = px.box(self.df, x='network', y='signal_strength',
                         title="Signal Strength Distribution by Network",
                         color='network')
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            fig = px.box(self.df, x='network', y='signal_quality',
                         title="Signal Quality Distribution by Network",
                         color='network')
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            fig = px.box(self.df, x='network', y='data_speed',
                         title="Data Speed Distribution by Network",
                         color='network')
            st.plotly_chart(fig, use_container_width=True)

        with tab4:
            fig = px.box(self.df, x='network', y='sinr',
                         title="SINR Distribution by Network",
                         color='network')
            st.plotly_chart(fig, use_container_width=True)

    def create_cost_benefit_analysis(self):
        """Feature 1: Cost-Benefit Analysis"""
        st.subheader("💰 Cost-Benefit Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.write("### Data Plan Prices (₦)")
            cost_data = self.generator.cost_data
            cost_df = pd.DataFrame(cost_data).T
            st.dataframe(cost_df.style.format("₦{:.0f}"), use_container_width=True)

        with col2:
            st.write("### Cost per Mbps Value")
            value_scores = {}
            for network in self.generator.networks:
                avg_speed = self.df[self.df['network'] == network]['data_speed'].mean()
                cost_per_gb = cost_data[network]["1GB"]
                value_score = (avg_speed / cost_per_gb) * 100
                value_scores[network] = value_score

            fig = px.bar(x=list(value_scores.keys()), y=list(value_scores.values()),
                         title="Value for Money Score (Higher is Better)",
                         labels={'x': 'Network', 'y': 'Value Score'})
            st.plotly_chart(fig, use_container_width=True)

    def create_reliability_scoring(self):
        """Feature 2: Network Reliability Scoring"""
        st.subheader("🛡️ Network Reliability Scoring")

        reliability_scores = {}

        for network in self.generator.networks:
            network_data = self.df[self.df['network'] == network]

            # Calculate reliability components
            consistency_score = (100 - network_data['signal_quality'].std()) * 0.3
            coverage_score = (network_data['signal_quality'] > 70).mean() * 100 * 0.4
            speed_stability = (100 - network_data['data_speed'].std()) * 0.3

            total_score = consistency_score + coverage_score + speed_stability
            reliability_scores[network] = {
                'total': total_score,
                'consistency': consistency_score,
                'coverage': coverage_score,
                'speed_stability': speed_stability
            }

        # Display reliability scores
        cols = st.columns(4)
        for idx, (network, scores) in enumerate(reliability_scores.items()):
            with cols[idx]:
                st.metric(
                    label=f"{network} Reliability",
                    value=f"{scores['total']:.1f}%",
                    delta=f"Consistency: {scores['consistency']:.1f}%"
                )

        # Reliability breakdown chart
        fig = go.Figure()
        for metric in ['consistency', 'coverage', 'speed_stability']:
            fig.add_trace(go.Bar(
                name=metric.title(),
                x=list(reliability_scores.keys()),
                y=[scores[metric] for scores in reliability_scores.values()]
            ))

        fig.update_layout(barmode='stack', title="Reliability Score Breakdown")
        st.plotly_chart(fig, use_container_width=True)

    def create_time_based_analysis(self):
        """Feature 3: Time-based Performance Analysis"""
        st.subheader("⏰ Time-based Performance Analysis")

        # Try to load time-based data, or simulate it
        try:
            time_df = pd.read_csv("futo_network_time_data.csv")
        except:
            # Simulate time-based data if file doesn't exist
            time_df = self.simulate_time_data()

        if not time_df.empty:
            # Create time performance chart
            time_avg = time_df.groupby(['time_of_day', 'network'])['data_speed'].mean().reset_index()
            fig = px.line(time_avg, x='time_of_day', y='data_speed', color='network',
                          title="Network Performance Throughout the Day",
                          labels={'time_of_day': 'Time of Day', 'data_speed': 'Data Speed (Mbps)'})
            st.plotly_chart(fig, use_container_width=True)

        # Peak hours analysis
        st.write("### 📊 Peak Hours Performance Drop")
        peak_drop = {}
        for network in self.generator.networks:
            network_data = self.df[self.df['network'] == network]
            avg_speed = network_data['data_speed'].mean()
            # Simulate peak hour drop (40% reduction during evening)
            peak_drop[network] = avg_speed * 0.4  # 40% performance drop

        fig = px.bar(x=list(peak_drop.keys()), y=list(peak_drop.values()),
                     title="Performance Drop During Peak Hours (Simulated)",
                     labels={'x': 'Network', 'y': 'Speed Reduction (Mbps)'})
        st.plotly_chart(fig, use_container_width=True)

    def simulate_time_data(self):
        """Simulate time-based data if not available"""
        times_of_day = ["morning", "afternoon", "evening", "night"]
        data = []

        for location in self.generator.locations[:5]:  # Sample locations for speed
            for network in self.generator.networks:
                for time_of_day in times_of_day:
                    base_speed = self.df[self.df['network'] == network]['data_speed'].mean()
                    # Apply time-based modifiers
                    time_factors = {"morning": 1.0, "afternoon": 0.8, "evening": 0.6, "night": 1.1}
                    speed = base_speed * time_factors[time_of_day] + np.random.normal(0, 2)

                    data.append({
                        'location': location,
                        'network': network,
                        'time_of_day': time_of_day,
                        'data_speed': max(1, speed)
                    })

        return pd.DataFrame(data)

    def create_live_performance_map(self):
        """Feature 5: Live Network Performance Map"""
        st.subheader("📡 Live Network Performance Map")

        # Map style selector - removed stamen-terrain
        col1, col2 = st.columns([3, 1])

        with col2:
            map_style = st.selectbox(
                "Choose Map Style:",
                ["open-street-map", "carto-positron", "carto-darkmatter", "stamen-toner", "white-bg"],
                index=0
            )

        # Option 1: Proper Interactive Map with Real FUTO Layout
        st.write("#### 🗺️ Interactive FUTO Campus Map")

        # FUTO main campus coordinates (more accurate)
        futo_center = [5.4074, 7.0716]  # More precise FUTO coordinates

        # Create performance data for the map
        performance_data = []
        for location, coords in self.location_coordinates.items():
            location_data = self.df[self.df['location'] == location]
            if len(location_data) > 0:
                avg_performance = location_data['signal_quality'].mean()
                best_network = self.get_best_network_per_location().get(location, "Unknown")

                performance_data.append({
                    'lat': coords['lat'],
                    'lon': coords['lon'],
                    'performance': avg_performance,
                    'location': location,
                    'best_network': best_network,
                    'avg_speed': location_data['data_speed'].mean(),
                    'signal_strength': location_data['signal_strength'].mean()
                })

        perf_df = pd.DataFrame(performance_data)

        if not perf_df.empty:
            # Handle white-bg style specially
            if map_style == "white-bg":
                map_style = "open-street-map"
                fig = px.scatter_mapbox(
                    perf_df,
                    lat='lat',
                    lon='lon',
                    color='performance',
                    size='performance',
                    hover_name='location',
                    hover_data={
                        'best_network': True,
                        'performance': ':.1f',
                        'avg_speed': ':.1f',
                        'signal_strength': ':.1f',
                        'lat': False,
                        'lon': False
                    },
                    color_continuous_scale="RdYlGn",
                    size_max=25,
                    zoom=16,
                    height=600,
                    title=f"FUTO Campus - Network Performance Heatmap"
                )
                fig.update_layout(mapbox_style="white-bg")
            else:
                fig = px.scatter_mapbox(
                    perf_df,
                    lat='lat',
                    lon='lon',
                    color='performance',
                    size='performance',  # Size based on performance
                    hover_name='location',
                    hover_data={
                        'best_network': True,
                        'performance': ':.1f',
                        'avg_speed': ':.1f',
                        'signal_strength': ':.1f',
                        'lat': False,
                        'lon': False
                    },
                    color_continuous_scale="RdYlGn",  # Red-Yellow-Green scale
                    size_max=25,
                    zoom=16,
                    height=600,
                    title=f"FUTO Campus - Network Performance Heatmap ({map_style.replace('-', ' ').title()})"
                )
                fig.update_layout(mapbox_style=map_style)

            # Update layout for better appearance
            fig.update_layout(
                mapbox=dict(
                    center=dict(lat=futo_center[0], lon=futo_center[1]),
                    zoom=16
                ),
                margin={"r": 0, "t": 50, "l": 0, "b": 0},
                coloraxis_colorbar=dict(
                    title="Signal Quality %",
                    thickness=20,
                    len=0.75
                )
            )

            # Add custom hover template
            fig.update_traces(
                hovertemplate=(
                    "<b>%{hovertext}</b><br><br>"
                    "Best Network: %{customdata[0]}<br>"
                    "Signal Quality: %{customdata[1]:.1f}%<br>"
                    "Avg Speed: %{customdata[2]:.1f} Mbps<br>"
                    "Signal Strength: %{customdata[3]:.1f} dBm"
                    "<extra></extra>"
                )
            )

            st.plotly_chart(fig, use_container_width=True)

        # Option 2: Network Coverage Summary
        st.write("#### 📊 Network Coverage Summary")

        col1, col2 = st.columns(2)

        with col1:
            # Best network by location count
            best_networks = self.get_best_network_per_location()
            network_counts = pd.Series(best_networks).value_counts()

            fig = px.pie(
                values=network_counts.values,
                names=network_counts.index,
                title="Locations Where Each Network is Best",
                color=network_counts.index,
                color_discrete_map={
                    'MTN': '#FF6B6B',
                    'Airtel': '#4ECDC4',
                    'Glo': '#45B7D1',
                    '9mobile': '#96CEB4'
                }
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Network performance by area type
            area_types = {
                "Academic": ["SENATE Building", "Library", "ICT", "SICT building", "SEET",
                             "SOHT building", "Sops building", "Lecture Hall 2"],
                "Hostels": ["Hostel A", "Hostel B", "Hostel C", "Hostel D", "Hostel E",
                            "PG Hostel", "750 caps", "1000 Caps"],
                "Administrative": ["Student Affairs", "UCC Centre", "FUTO Medicals", "NDDC", "TetFund"],
                "Social": ["Front Gate", "Back Gate", "Round About", "Futo Cafe", "Futo Park",
                           "Futo Garden", "ACE fuels", "Bj Services"]
            }

            area_data = []
            for area_type, locations in area_types.items():
                for location in locations:
                    loc_data = self.df[self.df['location'] == location]
                    if len(loc_data) > 0:
                        best_net = best_networks.get(location, "Unknown")
                        area_data.append({
                            'Area Type': area_type,
                            'Location': location,
                            'Best Network': best_net,
                            'Performance': loc_data['signal_quality'].mean()
                        })

            if area_data:
                area_df = pd.DataFrame(area_data)
                fig = px.box(area_df, x='Area Type', y='Performance', color='Area Type',
                             title="Network Performance Distribution by Area Type")
                st.plotly_chart(fig, use_container_width=True)

        # Option 3: Detailed Location Performance Table
        st.write("#### 📋 Detailed Location Performance")

        # Create summary table
        summary_data = []
        for location in self.generator.locations:
            location_data = self.df[self.df['location'] == location]
            if len(location_data) > 0:
                best_net = best_networks.get(location, "Unknown")
                avg_quality = location_data['signal_quality'].mean()
                avg_speed = location_data['data_speed'].mean()

                # Color code the performance level
                if avg_quality > 80:
                    performance_level = "🟢 Excellent"
                elif avg_quality > 60:
                    performance_level = "🟡 Good"
                elif avg_quality > 40:
                    performance_level = "🟠 Fair"
                else:
                    performance_level = "🔴 Poor"

                summary_data.append({
                    'Location': location,
                    'Best Network': best_net,
                    'Avg Signal Quality': f"{avg_quality:.1f}%",
                    'Avg Data Speed': f"{avg_speed:.1f} Mbps",
                    'Performance Level': performance_level
                })

        summary_df = pd.DataFrame(summary_data)

        # Add some styling to the dataframe
        st.dataframe(
            summary_df,
            use_container_width=True,
            height=400
        )

    def create_user_experience_ratings(self):
        """Feature 6: User Experience Ratings"""
        st.subheader("⭐ User Experience Ratings")

        # Simulate user ratings based on performance data
        user_ratings = {}
        for network in self.generator.networks:
            network_data = self.df[self.df['network'] == network]

            # Calculate ratings from performance metrics
            call_quality = (network_data['signal_quality'].mean() / 100) * 5
            data_speed_rating = (network_data['data_speed'].mean() / 50) * 5
            reliability_rating = (network_data['signal_quality'].std() / 20) * 5
            overall = (call_quality + data_speed_rating + (5 - reliability_rating)) / 3

            user_ratings[network] = {
                'Overall': min(5, overall),
                'Call Quality': min(5, call_quality),
                'Data Speed': min(5, data_speed_rating),
                'Reliability': min(5, 5 - reliability_rating)
            }

        # Display rating stars
        cols = st.columns(4)
        for idx, network in enumerate(self.generator.networks):
            with cols[idx]:
                rating = user_ratings[network]['Overall']
                st.write(f"**{network}**")
                stars = "⭐" * int(rating) + "☆" * (5 - int(rating))
                st.write(f"{stars} ({rating:.1f}/5)")
                st.caption(f"Speed: {user_ratings[network]['Data Speed']:.1f}⭐")

        # Detailed ratings radar chart
        fig = go.Figure()

        categories = ['Call Quality', 'Data Speed', 'Reliability']
        for network in self.generator.networks:
            fig.add_trace(go.Scatterpolar(
                r=[user_ratings[network][cat] for cat in categories],
                theta=categories,
                fill='toself',
                name=network
            ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            title="User Experience Ratings Comparison"
        )
        st.plotly_chart(fig, use_container_width=True)

        # User feedback simulation
        st.write("### 💬 Student Feedback Summary")
        feedback = {
            "MTN": "Reliable for video calls and streaming, but expensive",
            "Airtel": "Good balance of speed and reliability, works well indoors",
            "Glo": "Great for social media, poor in hostels and buildings",
            "9mobile": "Improving coverage, good customer service"
        }

        for network, comment in feedback.items():
            with st.expander(f"{network} Student Reviews"):
                st.write(comment)
                st.caption("Based on simulated student feedback data")

    def run_enhanced_dashboard(self):
        """Run the enhanced dashboard with all new features"""
        st.markdown('<div class="main-header">📶 FUTO Mobile Network Analysis Dashboard</div>', unsafe_allow_html=True)

        # Create tabs for better organization
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Overview", "💰 Cost Analysis", "🛡️ Reliability",
            "⏰ Time Analysis", "🗺️ Campus Maps", "⭐ User Experience"
        ])

        with tab1:
            # Keep original overview metrics
            self.create_overview_metrics()
            self.create_network_comparison_charts()

        with tab2:
            self.create_cost_benefit_analysis()

        with tab3:
            self.create_reliability_scoring()

        with tab4:
            self.create_time_based_analysis()

        with tab5:
            self.create_live_performance_map()

        with tab6:
            self.create_user_experience_ratings()


# Update the data generator with cost data
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

        # Add cost data
        self.cost_data = {
            "MTN": {"1GB": 300, "2GB": 500, "5GB": 1200, "10GB": 2000},
            "Airtel": {"1GB": 280, "2GB": 480, "5GB": 1150, "10GB": 1900},
            "Glo": {"1GB": 250, "2GB": 400, "5GB": 1000, "10GB": 1800},
            "9mobile": {"1GB": 270, "2GB": 450, "5GB": 1100, "10GB": 1850}
        }

    def generate_dataset(self, samples_per_location=10):
        """Generate sample dataset"""
        data = []
        for location in self.locations:
            for network in self.networks:
                for _ in range(samples_per_location):
                    # Simulate realistic data
                    base_strength = {"MTN": -75, "Airtel": -78, "Glo": -82, "9mobile": -85}[network]
                    strength = base_strength + np.random.normal(0, 5)
                    quality = max(0, min(100, 80 + np.random.normal(0, 15)))
                    speed = max(1,
                                {"MTN": 45, "Airtel": 40, "Glo": 25, "9mobile": 20}[network] + np.random.normal(0, 8))

                    data.append({
                        "location": location,
                        "network": network,
                        "signal_strength": round(strength, 1),
                        "signal_quality": round(quality, 1),
                        "data_speed": round(speed, 1),
                        "sinr": round(15 + np.random.normal(0, 3), 1)
                    })

        return pd.DataFrame(data)


# Run the enhanced dashboard
if __name__ == "__main__":
    dashboard = EnhancedFUTODashboard()
    dashboard.run_enhanced_dashboard()