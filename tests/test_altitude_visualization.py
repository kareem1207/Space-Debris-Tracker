import unittest
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
import seaborn as sns

# Add the parent directory to the path so we can import main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_satellite_position

class TestAltitudeVisualization(unittest.TestCase):
    """Test suite for altitude visualization with special test cases"""
    
    def setUp(self):
        """Set up mock satellite and observer objects for testing"""
        self.satellite = MockSatellite()
        self.observer = MockObserver()
        
        # Create directory for saving graphs if it doesn't exist
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_output")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def test_just_above_horizon_cases(self):
        """Test cases where the ISS is just above the horizon with small increments"""
        test_cases = [
            {"altitude": 0.1, "azimuth": 45},
            {"altitude": 0.5, "azimuth": 90},
            {"altitude": 1.0, "azimuth": 135},
            {"altitude": 1.5, "azimuth": 180},
            {"altitude": 2.0, "azimuth": 225},
            {"altitude": 2.5, "azimuth": 270},
            {"altitude": 3.0, "azimuth": 315},
            {"altitude": 4.0, "azimuth": 0},
            {"altitude": 5.0, "azimuth": 45},
        ]
        
        results = []
        for case in test_cases:
            self.satellite.altitude = case["altitude"]
            self.satellite.azimuth = case["azimuth"]
            
            result = get_satellite_position(self.satellite, self.observer)
            results.append({
                "input_alt": case["altitude"],
                "input_az": case["azimuth"],
                "output_alt_angle": result["altitude_angle"],
                "output_az_angle": result["azimuth_angle"],
                "alt_degrees": result["alt_degrees"],
                "az_degrees": result["az_degrees"],
                "is_visible": result["is_visible"]
            })
            
            # For very low altitudes, check that the minimum tracking angle is appropriate
            if case["altitude"] < 2.0:
                self.assertGreaterEqual(result["altitude_angle"], 5,
                                         f"Very low altitudes ({case['altitude']} deg) should be amplified")
        
        # Print results
        print("\nJust Above Horizon Test Results:")
        print("-" * 80)
        print(f"{'Input Alt':^10} | {'Input Az':^10} | {'Output Alt':^10} | {'Output Az':^10} | {'Visible':^10}")
        print("-" * 80)
        for result in results:
            print(f"{result['input_alt']:^10.1f} | {result['input_az']:^10.1f} | "
                  f"{result['output_alt_angle']:^10d} | {result['output_az_angle']:^10d} | "
                  f"{str(result['is_visible']):^10}")
        print("-" * 80)
        
        # Create visualization
        self._create_horizon_graph(results, "just_above_horizon_visualization.png")
        
        # Return results for potential further analysis
        return results
    
    def test_transition_cases(self):
        """Test cases where the ISS transitions from below horizon to above"""
        # Create a range of altitudes from -5° to +10° with 0.5° increments
        altitudes = np.arange(-5.0, 10.5, 0.5)
        azimuths = np.ones_like(altitudes) * 180  # Keep azimuth constant for this test
        
        results = []
        for alt, az in zip(altitudes, azimuths):
            self.satellite.altitude = alt
            self.satellite.azimuth = az
            
            result = get_satellite_position(self.satellite, self.observer)
            results.append({
                "input_alt": alt,
                "input_az": az,
                "output_alt_angle": result["altitude_angle"],
                "output_az_angle": result["azimuth_angle"],
                "alt_degrees": result["alt_degrees"],
                "az_degrees": result["az_degrees"],
                "is_visible": result["is_visible"]
            })
        
        # Print results
        print("\nHorizon Transition Test Results:")
        print("-" * 80)
        print(f"{'Input Alt':^10} | {'Output Alt':^10} | {'Visible':^10}")
        print("-" * 80)
        for result in results:
            print(f"{result['input_alt']:^10.1f} | {result['output_alt_angle']:^10d} | {str(result['is_visible']):^10}")
        print("-" * 80)
        
        # Create visualization
        self._create_transition_graph(results, "horizon_transition_visualization.png")
        
        # Return results for potential further analysis
        return results
    
    def test_full_sky_coverage(self):
        """Test cases covering the full visible sky with various altitude/azimuth combinations"""
        # Create a grid of test points covering the visible sky
        # Altitudes from 0° to 90° (horizon to zenith)
        # Azimuths from 0° to 359°
        altitudes = np.linspace(0, 90, 10)
        azimuths = np.linspace(0, 359, 12)
        
        # Create a grid of combinations
        alt_grid, az_grid = np.meshgrid(altitudes, azimuths)
        alt_flat = alt_grid.flatten()
        az_flat = az_grid.flatten()
        
        results = []
        for alt, az in zip(alt_flat, az_flat):
            self.satellite.altitude = alt
            self.satellite.azimuth = az
            
            result = get_satellite_position(self.satellite, self.observer)
            results.append({
                "input_alt": alt,
                "input_az": az,
                "output_alt_angle": result["altitude_angle"],
                "output_az_angle": result["azimuth_angle"],
                "alt_degrees": result["alt_degrees"],
                "az_degrees": result["az_degrees"],
                "is_visible": result["is_visible"]
            })
        
        # Print summary
        visible_count = sum(1 for r in results if r["is_visible"])
        print(f"\nFull Sky Coverage Test:")
        print(f"Total test points: {len(results)}")
        print(f"Visible points: {visible_count}")
        print(f"Visibility percentage: {visible_count / len(results) * 100:.1f}%")
        
        # Create visualization
        self._create_sky_coverage_graph(results, "full_sky_coverage_visualization.png")
        
        # Return results for potential further analysis
        return results
    
    def test_special_cases(self):
        """Special test cases showing particular scenarios"""
        test_cases = [
            {"name": "Just visible", "altitude": 0.01, "azimuth": 90},
            {"name": "Borderline", "altitude": 0.001, "azimuth": 90},
            {"name": "Low altitude, north", "altitude": 3.0, "azimuth": 0},
            {"name": "Low altitude, east", "altitude": 3.0, "azimuth": 90},
            {"name": "Low altitude, south", "altitude": 3.0, "azimuth": 180},
            {"name": "Low altitude, west", "altitude": 3.0, "azimuth": 270},
            {"name": "Medium altitude", "altitude": 30.0, "azimuth": 125},
            {"name": "High altitude", "altitude": 60.0, "azimuth": 210},
            {"name": "Near zenith", "altitude": 85.0, "azimuth": 45},
            {"name": "Zenith", "altitude": 90.0, "azimuth": 0},
        ]
        
        results = []
        for case in test_cases:
            self.satellite.altitude = case["altitude"]
            self.satellite.azimuth = case["azimuth"]
            
            result = get_satellite_position(self.satellite, self.observer)
            results.append({
                "name": case["name"],
                "input_alt": case["altitude"],
                "input_az": case["azimuth"],
                "output_alt_angle": result["altitude_angle"],
                "output_az_angle": result["azimuth_angle"],
                "alt_degrees": result["alt_degrees"],
                "az_degrees": result["az_degrees"],
                "is_visible": result["is_visible"]
            })
        
        # Print results
        print("\nSpecial Test Cases:")
        print("-" * 120)
        print(f"{'Case':^20} | {'Input Alt':^10} | {'Input Az':^10} | {'Output Alt':^10} | {'Output Az':^10} | {'Visible':^10}")
        print("-" * 120)
        for result in results:
            print(f"{result['name']:^20} | {result['input_alt']:^10.3f} | {result['input_az']:^10.1f} | "
                  f"{result['output_alt_angle']:^10d} | {result['output_az_angle']:^10d} | "
                  f"{str(result['is_visible']):^10}")
        print("-" * 120)
        
        # Create visualization
        self._create_special_cases_graph(results, "special_cases_visualization.png")
        
        # Return results for potential further analysis
        return results
    
    def _create_horizon_graph(self, results, filename):
        """Create a graph showing the amplification of angles near the horizon"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
        fig.suptitle('Just Above Horizon Test Cases', fontsize=16)
        
        # Extract data
        input_alts = [r['input_alt'] for r in results]
        output_alts = [r['output_alt_angle'] for r in results]
        input_azs = [r['input_az'] for r in results]
        output_azs = [r['output_az_angle'] for r in results]
        
        # Plot altitude transformation
        ax1.plot(input_alts, output_alts, 'o-', color='blue', markersize=8, label='Servo Angle')
        ax1.plot(input_alts, input_alts, '--', color='gray', label='1:1 Reference')
        ax1.plot(input_alts, [i*2 for i in input_alts], '--', color='green', label='2:1 Reference')
        
        # Add minimum threshold line
        min_threshold = 5
        ax1.axhline(y=min_threshold, color='red', linestyle='--', label=f'Min Threshold ({min_threshold}°)')
        
        ax1.set_xlabel('Input Altitude (degrees)')
        ax1.set_ylabel('Output Altitude Angle (degrees)')
        ax1.set_title('Altitude Angle Transformation for Low Altitudes')
        ax1.grid(True)
        ax1.legend()
        
        # Add annotations for key points
        for i, r in enumerate(results):
            if i % 2 == 0:  # Skip some points for clarity
                ax1.annotate(f"{r['input_alt']}°→{r['output_alt_angle']}°",
                           (r['input_alt'], r['output_alt_angle']),
                           textcoords="offset points", xytext=(0,10),
                           ha='center', fontsize=8)
        
        # Plot servo angles on polar plot
        ax2 = plt.subplot(212, projection='polar')
        for r in results:
            # Convert to radians for polar plot
            az_rad = np.radians(r['input_az'])
            alt = r['input_alt']
            
            # Mark the position
            ax2.plot(az_rad, alt, 'o', markersize=10, 
                    color='blue' if r['is_visible'] else 'gray')
            
            # Add text annotation for altitude
            ax2.annotate(f"{alt}°", 
                       (az_rad, alt),
                       textcoords="offset points", xytext=(5, 5), 
                       fontsize=8)
        
        # Set polar plot properties
        ax2.set_theta_zero_location('N')  # 0 degrees at the top (North)
        ax2.set_theta_direction(-1)  # Clockwise
        ax2.set_rlim(0, 10)  # Limit to low altitude range
        ax2.set_title('Low Altitude Positions in Sky')
        ax2.grid(True)
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(os.path.join(self.output_dir, filename))
        print(f"\nGraph saved to {os.path.join(self.output_dir, filename)}")
        
    def _create_transition_graph(self, results, filename):
        """Create a graph showing the transition from below to above horizon"""
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))
        fig.suptitle('ISS Horizon Transition Visualization', fontsize=16)
        
        # Extract data
        input_alts = [r['input_alt'] for r in results]
        output_alts = [r['output_alt_angle'] for r in results]
        visibility = [1 if r['is_visible'] else 0 for r in results]
        
        # Plot 1: Input vs Output altitude
        ax1.plot(input_alts, output_alts, 'o-', color='blue', markersize=8)
        ax1.axhline(y=0, color='gray', linestyle='--')
        ax1.axvline(x=0, color='red', linestyle='--', label='Horizon')
        
        # Color the background to indicate visibility zones
        ax1.axvspan(0, max(input_alts), alpha=0.2, color='green', label='Visible')
        ax1.axvspan(min(input_alts), 0, alpha=0.2, color='gray', label='Not Visible')
        
        ax1.set_xlabel('Actual Altitude (degrees)')
        ax1.set_ylabel('Servo Angle (degrees)')
        ax1.set_title('Servo Angle vs. Actual Altitude')
        ax1.grid(True)
        ax1.legend()
        
        # Plot 2: Visibility transition
        ax2.plot(input_alts, visibility, 'o-', color='green', markersize=8)
        ax2.axvline(x=0, color='red', linestyle='--', label='Horizon')
        ax2.fill_between(input_alts, 0, visibility, color='green', alpha=0.3)
        
        ax2.set_xlabel('Altitude (degrees)')
        ax2.set_ylabel('Visibility')
        ax2.set_yticks([0, 1])
        ax2.set_yticklabels(['Not Visible', 'Visible'])
        ax2.set_title('Visibility Transition at Horizon')
        ax2.grid(True)
        
        # Plot 3: Close-up of the amplification near horizon
        visible_results = [r for r in results if r['is_visible']]
        if visible_results:
            visible_inputs = [r['input_alt'] for r in visible_results]
            visible_outputs = [r['output_alt_angle'] for r in visible_results]
            
            ax3.plot(visible_inputs, visible_outputs, 'o-', color='blue', 
                    markersize=8, label='Servo Angle')
            
            # Add reference lines
            ax3.plot(visible_inputs, visible_inputs, '--', color='gray', label='1:1 Reference')
            ax3.plot(visible_inputs, [alt*2 for alt in visible_inputs], '--', 
                    color='green', label='2:1 Amplification')
            
            # Add minimum threshold line if applicable
            min_threshold = 5
            ax3.axhline(y=min_threshold, color='red', linestyle='--', 
                       label=f'Min Threshold ({min_threshold}°)')
            
            # Mark the ranges for special handling
            ax3.axvspan(0, 2.0, alpha=0.1, color='red', label='Special Treatment <2°')
            ax3.axvspan(2.0, 5.0, alpha=0.1, color='orange', label='Low Altitude 2-5°')
            
            ax3.set_xlabel('Visible Altitude (degrees)')
            ax3.set_ylabel('Servo Angle (degrees)')
            ax3.set_title('Altitude Amplification for Visible Positions')
            ax3.grid(True)
            ax3.legend(loc='upper left')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(os.path.join(self.output_dir, filename))
        print(f"\nGraph saved to {os.path.join(self.output_dir, filename)}")
    
    def _create_sky_coverage_graph(self, results, filename):
        """Create a graph showing the coverage of the sky"""
        fig = plt.figure(figsize=(18, 12))
        gs = GridSpec(2, 3, figure=fig)
        fig.suptitle('Full Sky Coverage Visualization', fontsize=16)
        
        # Extract data
        input_alts = np.array([r['input_alt'] for r in results])
        input_azs = np.array([r['input_az'] for r in results])
        output_alts = np.array([r['output_alt_angle'] for r in results])
        output_azs = np.array([r['output_az_angle'] for r in results])
        visibility = np.array([1 if r['is_visible'] else 0 for r in results])
        
        # Plot 1: Sky plot (polar)
        ax1 = fig.add_subplot(gs[0, 0], projection='polar')
        # Convert to radians and invert radius (90° at center, 0° at edge)
        az_rads = np.radians(input_azs)
        # For polar plot: 90° altitude at center, 0° at edge
        alt_radius = 90 - input_alts
        
        scatter = ax1.scatter(az_rads, alt_radius, c=output_alts, 
                             cmap='viridis', s=50, alpha=0.7)
        
        # Set polar plot properties
        ax1.set_theta_zero_location('N')  # 0 degrees at the top (North)
        ax1.set_theta_direction(-1)       # Clockwise
        ax1.set_rticks([0, 15, 30, 45, 60, 75, 90])  # Radial ticks
        ax1.set_yticklabels(['90°', '75°', '60°', '45°', '30°', '15°', '0°'])  # Altitude labels
        ax1.set_rlim(0, 90)
        ax1.set_title('Sky Coverage - Servo Altitude Angles')
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax1, pad=0.1)
        cbar.set_label('Servo Altitude Angle')
        
        # Plot 2: Input vs Output altitude
        ax2 = fig.add_subplot(gs[0, 1])
        scatter2 = ax2.scatter(input_alts, output_alts, c=input_azs, cmap='twilight', s=50, alpha=0.7)
        
        # Add reference lines
        ax2.plot([0, 90], [0, 180], '--', color='gray', label='Linear Mapping')
        
        ax2.set_xlabel('Input Altitude (degrees)')
        ax2.set_ylabel('Output Servo Angle (degrees)')
        ax2.set_title('Altitude Angle Transformation')
        ax2.grid(True)
        ax2.legend()
        
        # Add colorbar
        cbar2 = plt.colorbar(scatter2, ax=ax2)
        cbar2.set_label('Azimuth (degrees)')
        
        # Plot 3: Input vs Output azimuth
        ax3 = fig.add_subplot(gs[0, 2])
        scatter3 = ax3.scatter(input_azs, output_azs, c=input_alts, cmap='viridis', s=50, alpha=0.7)
        
        # Add reference line
        ax3.plot([0, 360], [0, 180], '--', color='gray', label='Linear Mapping')
        
        ax3.set_xlabel('Input Azimuth (degrees)')
        ax3.set_ylabel('Output Servo Angle (degrees)')
        ax3.set_title('Azimuth Angle Transformation')
        ax3.grid(True)
        ax3.legend()
        
        # Add colorbar
        cbar3 = plt.colorbar(scatter3, ax=ax3)
        cbar3.set_label('Altitude (degrees)')
        
        # Plot 4: 3D visualization
        ax4 = fig.add_subplot(gs[1, :], projection='3d')
        
        # Convert to Cartesian coordinates for 3D plot
        x = np.sin(np.radians(90 - input_alts)) * np.cos(np.radians(input_azs))
        y = np.sin(np.radians(90 - input_alts)) * np.sin(np.radians(input_azs))
        z = np.cos(np.radians(90 - input_alts))
        
        # Create a sphere for reference
        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        sphere_x = 0.99 * np.cos(u) * np.sin(v)
        sphere_y = 0.99 * np.sin(u) * np.sin(v)
        sphere_z = 0.99 * np.cos(v)
        ax4.plot_surface(sphere_x, sphere_y, sphere_z, color="gray", alpha=0.1)
        
        # Plot points
        visible_mask = (visibility == 1)
        if np.any(visible_mask):
            scatter4 = ax4.scatter(x[visible_mask], y[visible_mask], z[visible_mask], 
                               c=output_alts[visible_mask], cmap='viridis', s=50, label='Visible')
        
        if np.any(~visible_mask):
            ax4.scatter(x[~visible_mask], y[~visible_mask], z[~visible_mask], 
                      color='gray', s=30, alpha=0.3, label='Not Visible')
        
        # Add reference axis
        ax4.plot([0, 1.1], [0, 0], [0, 0], 'r-', alpha=0.5, lw=1)  # x-axis (East)
        ax4.plot([0, 0], [0, 1.1], [0, 0], 'g-', alpha=0.5, lw=1)  # y-axis (North)
        ax4.plot([0, 0], [0, 0], [0, 1.1], 'b-', alpha=0.5, lw=1)  # z-axis (Up)
        
        # Add labels
        ax4.text(1.15, 0, 0, "East", color='red')
        ax4.text(0, 1.15, 0, "North", color='green')
        ax4.text(0, 0, 1.15, "Zenith", color='blue')
        
        # Draw the horizon plane
        xx, yy = np.meshgrid(np.linspace(-1, 1, 10), np.linspace(-1, 1, 10))
        zz = np.zeros_like(xx)
        ax4.plot_surface(xx, yy, zz, color="gray", alpha=0.1)
        
        ax4.set_title('3D Visualization of Sky Coverage')
        ax4.set_xlabel('X (East/West)')
        ax4.set_ylabel('Y (North/South)')
        ax4.set_zlabel('Z (Altitude)')
        ax4.legend()
        
        # Equal aspect ratio for 3D plot
        ax4.set_box_aspect([1,1,1])
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(os.path.join(self.output_dir, filename))
        print(f"\nGraph saved to {os.path.join(self.output_dir, filename)}")
    
    def _create_special_cases_graph(self, results, filename):
        """Create a visualization for special test cases"""
        fig = plt.figure(figsize=(15, 14))
        gs = GridSpec(2, 2, figure=fig)
        fig.suptitle('Special Test Cases Visualization', fontsize=16)
        
        # Extract data
        names = [r['name'] for r in results]
        input_alts = [r['input_alt'] for r in results]
        input_azs = [r['input_az'] for r in results]
        output_alts = [r['output_alt_angle'] for r in results]
        output_azs = [r['output_az_angle'] for r in results]
        visibility = [r['is_visible'] for r in results]
        
        # Plot 1: Case comparison bar chart
        ax1 = fig.add_subplot(gs[0, 0])
        
        # Visible cases only
        visible_indices = [i for i, v in enumerate(visibility) if v]
        visible_names = [names[i] for i in visible_indices]
        visible_input_alts = [input_alts[i] for i in visible_indices]
        visible_output_alts = [output_alts[i] for i in visible_indices]
        
        x = np.arange(len(visible_names))
        width = 0.35
        
        # Plot bars
        bar1 = ax1.bar(x - width/2, visible_input_alts, width, label='Input Altitude', color='skyblue')
        bar2 = ax1.bar(x + width/2, visible_output_alts, width, label='Servo Angle', color='coral')
        
        # Add labels and legend
        ax1.set_ylabel('Degrees')
        ax1.set_title('Altitude vs Servo Angle for Special Cases')
        ax1.set_xticks(x)
        ax1.set_xticklabels(visible_names, rotation=45, ha='right')
        ax1.legend()
        
        # Add value labels on top of bars
        def add_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax1.annotate(f'{height:.1f}' if height < 10 else f'{int(height)}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),  # 3 points vertical offset
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=8)
        
        add_labels(bar1)
        add_labels(bar2)
        
        # Plot 2: Sky plot with special cases
        ax2 = fig.add_subplot(gs[0, 1], projection='polar')
        
        # Create reference grid for the sky
        alts = np.linspace(0, 90, 7)  # 0, 15, 30, ..., 90
        azs = np.linspace(0, 2*np.pi, 13)  # 0, 30, 60, ..., 360 degrees
        
        # Plot altitude circles
        for alt in alts:
            radius = 90 - alt
            circle = plt.Circle((0, 0), radius, transform=ax2.transData._b, 
                              fill=False, color='gray', alpha=0.2)
            ax2.add_patch(circle)
            if alt > 0:  # Don't label the outer edge (0 degrees)
                ax2.text(np.pi/4, radius, f"{alt:g}°", color='gray', ha='left', va='bottom', alpha=0.7)
        
        # Plot azimuth lines
        for az in azs:
            ax2.plot([az, az], [0, 90], color='gray', alpha=0.2, linestyle='-', linewidth=0.5)
        
        # Add cardinal directions
        ax2.text(0, 91, "N", ha='center', va='center', fontweight='bold')
        ax2.text(np.pi/2, 91, "E", ha='center', va='center', fontweight='bold')
        ax2.text(np.pi, 91, "S", ha='center', va='center', fontweight='bold')
        ax2.text(3*np.pi/2, 91, "W", ha='center', va='center', fontweight='bold')
        
        # Plot special cases
        colors = plt.cm.tab10(np.linspace(0, 1, len(results)))
        
        for i, result in enumerate(results):
            if result['is_visible']:
                az_rad = np.radians(result['input_az'])
                # Convert altitude to radius (90° at center, 0° at edge)
                radius = 90 - result['input_alt']
                
                # Plot point
                ax2.plot(az_rad, radius, 'o', markersize=10, color=colors[i])
                
                # Add label with case name
                ax2.annotate(result['name'], 
                           (az_rad, radius),
                           xytext=(10, 10), textcoords='offset points',
                           color=colors[i], fontweight='bold',
                           arrowprops=dict(arrowstyle='->', color=colors[i]))
        
        # Set polar plot properties
        ax2.set_theta_zero_location('N')  # 0 degrees at the top (North)
        ax2.set_theta_direction(-1)       # Clockwise
        ax2.set_rticks([])                # Hide the radial ticks
        ax2.set_rmax(90)
        ax2.set_title('Special Cases in Sky View (Altitude as radius from center)')
        
        # Plot 3: Altitude transformation curve
        ax3 = fig.add_subplot(gs[1, 0])
        
        # Generate a smooth curve of altitude mappings
        alt_range = np.linspace(0, 90, 1000)
        servo_angles = []
        
        test_satellite = MockSatellite()
        test_satellite.azimuth = 180  # Arbitrary value
        
        for alt in alt_range:
            test_satellite.altitude = alt
            result = get_satellite_position(test_satellite, self.observer)
            servo_angles.append(result['altitude_angle'])
        
        # Plot the curve
        ax3.plot(alt_range, servo_angles, '-', color='blue', linewidth=2)
        
        # Mark the special cases
        for result in results:
            if result['is_visible']:
                ax3.plot(result['input_alt'], result['output_alt_angle'], 'o', 
                        markersize=8, label=result['name'])
                
                # Add annotation
                ax3.annotate(result['name'],
                           (result['input_alt'], result['output_alt_angle']),
                           xytext=(10, 0), textcoords='offset points',
                           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=.2'))
        
        # Add reference line
        ax3.plot([0, 90], [0, 180], '--', color='gray', label='Linear 2:1 Mapping')
        
        # Mark the amplification zones
        ax3.axvspan(0, 2, alpha=0.1, color='red', label='Special amplification <2°')
        ax3.axvspan(2, 5, alpha=0.1, color='orange', label='Low altitude 2-5°')
        
        ax3.set_xlabel('Input Altitude (degrees)')
        ax3.set_ylabel('Servo Angle (degrees)')
        ax3.set_title('Altitude to Servo Angle Transformation Curve')
        ax3.grid(True)
        ax3.legend(loc='upper left', fontsize=8)
        
        # Plot 4: Azimuth visualization
        ax4 = fig.add_subplot(gs[1, 1])
        
        # Prepare data for visible points
        visible_input_azs = [input_azs[i] for i, v in enumerate(visibility) if v]
        visible_output_azs = [output_azs[i] for i, v in enumerate(visibility) if v]
        visible_names = [names[i] for i, v in enumerate(visibility) if v]
        
        # Create azimuth circle visualization
        circle = plt.Circle((0, 0), 0.8, fill=False, color='black')
        ax4.add_artist(circle)
        
        # Add reference markings for compass directions
        for angle, label in [(0, 'N'), (90, 'E'), (180, 'S'), (270, 'W')]:
            rad = np.radians(angle)
            ax4.plot([0, np.cos(rad)], [0, np.sin(rad)], 'k--', alpha=0.3)
            ax4.text(1.1*np.cos(rad), 1.1*np.sin(rad), label, ha='center', va='center', fontweight='bold')
        
        # Plot the servo position mapping
        for i, (az, servoAz, name) in enumerate(zip(visible_input_azs, visible_output_azs, visible_names)):
            az_rad = np.radians(az)
            servo_rad = np.radians(servoAz * 2)  # Multiply by 2 to get 0-360 range
            
            # Plot point on the input circle (Actual azimuth)
            x_in = 0.8 * np.cos(az_rad)
            y_in = 0.8 * np.sin(az_rad)
            ax4.plot(x_in, y_in, 'o', markersize=8, color=colors[i])
            
            # Plot point on the output circle (Servo azimuth)
            x_out = 0.4 * np.cos(servo_rad)
            y_out = 0.4 * np.sin(servo_rad)
            ax4.plot(x_out, y_out, 's', markersize=6, color=colors[i])
            
            # Connect with arrow
            ax4.annotate('', xy=(x_out, y_out), xytext=(x_in, y_in),
                        arrowprops=dict(arrowstyle='->', color=colors[i]))
            
            # Add name label
            if i % 2 == 0:  # Alternate position to avoid overlap
                ax4.annotate(name, xy=(x_in, y_in), xytext=(15, 15), 
                           textcoords='offset points', color=colors[i])
            else:
                ax4.annotate(name, xy=(x_in, y_in), xytext=(-15, -15), 
                           textcoords='offset points', color=colors[i])
        
        # Add legend explaining the circles
        center_point = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='black', markersize=10, label='Center')
        input_circle = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='Actual Azimuth')
        output_circle = plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='red', markersize=8, label='Servo Azimuth')
        ax4.legend(handles=[input_circle, output_circle, center_point], loc='lower right')
        
        # Add inner circle for servo positions
        inner_circle = plt.Circle((0, 0), 0.4, fill=False, color='blue', linestyle='--')
        ax4.add_artist(inner_circle)
        
        ax4.set_xlim(-1.2, 1.2)
        ax4.set_ylim(-1.2, 1.2)
        ax4.set_aspect('equal')
        ax4.grid(True)
        ax4.set_title('Azimuth Mapping Visualization')
        ax4.set_xlabel('East/West')
        ax4.set_ylabel('North/South')
        ax4.set_xticks([])
        ax4.set_yticks([])
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(os.path.join(self.output_dir, filename))
        print(f"\nGraph saved to {os.path.join(self.output_dir, filename)}")

class MockSatellite:
    """Mock satellite object for testing"""
    def __init__(self):
        self.altitude = 0
        self.azimuth = 0
        
    def __sub__(self, observer):
        return MockDifference(self.altitude, self.azimuth)

class MockObserver:
    """Mock observer object for testing"""
    pass

class MockDifference:
    """Mock difference object for testing"""
    def __init__(self, altitude, azimuth):
        self.altitude = altitude
        self.azimuth = azimuth
    
    def at(self, time):
        return MockTopocentric(self.altitude, self.azimuth)

class MockTopocentric:
    """Mock topocentric object for testing"""
    def __init__(self, altitude, azimuth):
        self.altitude = altitude
        self.azimuth = azimuth
    
    def altaz(self):
        return MockAlt(self.altitude), MockAz(self.azimuth), MockDistance()

class MockAlt:
    """Mock altitude object for testing"""
    def __init__(self, degrees):
        self.degrees = degrees

class MockAz:
    """Mock azimuth object for testing"""
    def __init__(self, degrees):
        self.degrees = degrees

class MockDistance:
    """Mock distance object for testing"""
    def __init__(self):
        self.km = 400  # Typical ISS altitude

if __name__ == "__main__":
    unittest.main()