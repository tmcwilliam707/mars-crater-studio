import React, { useEffect, useState, useRef } from 'react';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { PolarArea, Bar } from 'react-chartjs-2';
import Papa from 'papaparse';
import gsap from 'gsap';
import {
  Chart as ChartJS,
  RadialLinearScale,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
} from 'chart.js';
import './CraterScene.css';
import './App.css';

// Register Chart.js components
ChartJS.register(RadialLinearScale, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const App = () => {
  const containerRef = useRef(null);
  const bannerRef = useRef(null);
  const [diameterChartData, setDiameterChartData] = useState(null);
  const [depthChartData, setDepthChartData] = useState(null);
  const [barChartData, setBarChartData] = useState(null);
  const [tableData, setTableData] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const container = containerRef.current;
    const banner = bannerRef.current;
    if (!container || !banner) return;

    // Three.js Scene Setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, banner.clientWidth / banner.clientHeight, 0.1, 1000);
    camera.position.set(0, 1, 5);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(banner.clientWidth, banner.clientHeight);
    banner.appendChild(renderer.domElement);

    const textureLoader = new THREE.TextureLoader();
    textureLoader.load(
      '/images/banner.jpg', // Correct background image for banner
      (texture) => {
        scene.background = texture;
      },
      undefined,
      (err) => console.error('Texture load error:', err)
    );

    const light = new THREE.HemisphereLight(0xffffff, 0x444444);
    light.position.set(0, 1, 0);
    scene.add(light);

    // Load BB-8 Model
    const loader = new GLTFLoader();
    loader.load('/models/bb8_animated.glb', (gltf) => {
      const bb8 = gltf.scene;
      bb8.position.set(-5, 0, 0); // Start position off-screen
      bb8.scale.set(4, 4, 4); // Scale BB-8 to be four times bigger
      scene.add(bb8);

      // Animate BB-8 across the banner
      gsap.to(bb8.position, {
        x: 5, // End position off-screen
        duration: 10,
        ease: 'power1.inOut',
        repeat: -1,
        yoyo: true,
      });
    }, undefined, (error) => {
      console.error('An error occurred while loading the BB-8 model:', error);
    });

    const animate = () => {
      requestAnimationFrame(animate);
      renderer.render(scene, camera);
    };
    animate();

    // Load CSV Data from public/data/
    fetch('/mean_stats_summary.csv')
      .then(response => {
        if (!response.ok) throw new Error(`CSV fetch failed: ${response.status}`);
        return response.text();
      })
      .then(csvText => {
        Papa.parse(csvText, {
          header: true,
          skipEmptyLines: true,
          complete: (result) => {
            const data = result.data[0];
            if (!data) {
              setError('No data found in CSV');
              return;
            }

            // Extract statistics from CSV data
            const meanDiameter = parseFloat(data.mean_diameter_km);
            const medianDiameter = parseFloat(data.median_diameter_km);
            const minDiameter = parseFloat(data.min_diameter_km);
            const maxDiameter = parseFloat(data.max_diameter_km);
            const meanDepth = parseFloat(data.mean_depth_km);
            const medianDepth = parseFloat(data.median_depth_km);
            const minDepth = parseFloat(data.min_depth_km);
            const maxDepth = parseFloat(data.max_depth_km);
            const meanCircularity = parseFloat(data.mean_circularity);

            // Set table data
            setTableData([
              { label: 'Mean Diameter (km)', value: meanDiameter },
              { label: 'Median Diameter (km)', value: medianDiameter },
              { label: 'Min Diameter (km)', value: minDiameter },
              { label: 'Max Diameter (km)', value: maxDiameter },
              { label: 'Mean Depth (km)', value: meanDepth },
              { label: 'Median Depth (km)', value: medianDepth },
              { label: 'Min Depth (km)', value: minDepth },
              { label: 'Max Depth (km)', value: maxDepth },
              { label: 'Mean Circularity', value: meanCircularity },
            ]);

            // Chart data for diameter visualization
            setDiameterChartData({
              labels: ['Mean Diameter (km)', 'Median Diameter (km)', 'Min Diameter (km)', 'Max Diameter (km)'],
              datasets: [{
                label: 'Diameter (km)',
                data: [meanDiameter, medianDiameter, minDiameter, maxDiameter],
                backgroundColor: [
                  'rgba(255, 99, 132, 0.2)',
                  'rgba(54, 162, 235, 0.2)',
                  'rgba(255, 206, 86, 0.2)',
                  'rgba(75, 192, 192, 0.2)',
                ],
                borderColor: [
                  'rgba(255, 99, 132, 1)',
                  'rgba(54, 162, 235, 1)',
                  'rgba(255, 206, 86, 1)',
                  'rgba(75, 192, 192, 1)',
                ],
                borderWidth: 1,
              }],
            });

            // Chart data for depth visualization
            setDepthChartData({
              labels: ['Mean Depth (km)', 'Median Depth (km)', 'Min Depth (km)', 'Max Depth (km)'],
              datasets: [{
                label: 'Depth (km)',
                data: [meanDepth, medianDepth, minDepth, maxDepth],
                backgroundColor: [
                  'rgba(153, 102, 255, 0.2)',
                  'rgba(255, 159, 64, 0.2)',
                  'rgba(75, 192, 192, 0.2)',
                  'rgba(255, 99, 132, 0.2)',
                ],
                borderColor: [
                  'rgba(153, 102, 255, 1)',
                  'rgba(255, 159, 64, 1)',
                  'rgba(75, 192, 192, 1)',
                  'rgba(255, 99, 132, 1)',
                ],
                borderWidth: 1,
              }],
            });

            // Chart data for all statistics visualization
            setBarChartData({
              labels: ['Mean Diameter (km)', 'Median Diameter (km)', 'Min Diameter (km)', 'Max Diameter (km)', 'Mean Depth (km)', 'Median Depth (km)', 'Min Depth (km)', 'Max Depth (km)', 'Mean Circularity'],
              datasets: [{
                label: 'Statistics',
                data: [meanDiameter, medianDiameter, minDiameter, maxDiameter, meanDepth, medianDepth, minDepth, maxDepth, meanCircularity],
                backgroundColor: 'rgba(0, 255, 255, 0.2)',
                borderColor: 'rgba(0, 255, 255, 1)',
                borderWidth: 1,
              }],
            });
          },
          error: (err) => setError(`CSV parsing error: ${err.message}`),
        });
      })
      .catch(err => setError(`Fetch error: ${err.message}`));
  }, []);

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: { color: '#FFD700' },  // Gold text
      },
      tooltip: {
        backgroundColor: 'rgba(139, 69, 19, 0.8)',
        titleColor: '#FFD700',
        bodyColor: '#FFD700',
      },
    },
    scales: {
      r: {
        angleLines: {
          color: 'rgba(255, 215, 0, 0.2)', // Gold color
        },
        grid: {
          color: 'rgba(255, 215, 0, 0.2)', // Gold color
        },
        pointLabels: {
          color: '#FFD700', // Gold color
          font: {
            size: 18, // Increase the font size for point labels
          },
        },
        ticks: {
          font: {
            size: 16, // Increase the font size for ticks
          },
        },
      },
    },
    maintainAspectRatio: false, // Allow the charts to take up more space
  };

  const barChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: { color: '#FFD700' },  // Gold text
      },
      tooltip: {
        backgroundColor: 'rgba(139, 69, 19, 0.8)',
        titleColor: '#FFD700',
        bodyColor: '#FFD700',
      },
    },
    scales: {
      x: {
        ticks: {
          color: '#FFD700', // Gold color
          font: {
            size: 16, // Increase the font size for x-axis ticks
          },
        },
        grid: {
          color: 'rgba(255, 215, 0, 0.2)', // Gold color
        },
      },
      y: {
        ticks: {
          color: '#FFD700', // Gold color
          font: {
            size: 16, // Increase the font size for y-axis ticks
          },
        },
        grid: {
          color: 'rgba(255, 215, 0, 0.2)', // Gold color
        },
      },
    },
    maintainAspectRatio: false, // Allow the charts to take up more space
  };

  return (
    <div ref={containerRef} className="crater-scene-container">
      <div ref={bannerRef} className="banner" style={{ backgroundImage: "url('/images/banner.jpg')" }}>
        <div className="title-overlay">MARS CRATER STUDIO</div>
      </div>
      <div className="link-container">
        <button onClick={() => window.location.href='https://github.com/tmcwilliam707/mars-crater-studio'}>Link to Dataset</button>
      </div>
      <div className="small-title">Taylor McWilliam circa 2025</div>
      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}
      {diameterChartData && depthChartData && barChartData ? (
        <div className="chart-overlay">
          <div className="chart-container">
            <PolarArea data={diameterChartData} options={chartOptions} />
          </div>
          <div className="chart-container">
            <PolarArea data={depthChartData} options={chartOptions} />
          </div>
          <div className="chart-container">
            <Bar data={barChartData} options={barChartOptions} />
          </div>
        </div>
      ) : !error && (
        <div className="loading-message">
          Loading crater data...
        </div>
      )}
      <div className="content" style={{ backgroundImage: "url('/images/starry.jpg')" }}>
        <p>Explore the fascinating world of Mars craters with detailed statistics and visualizations.</p>
      </div>
      <div className="data-table">
        <table>
          <thead>
            <tr>
              <th>Statistic</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            {tableData.map((row, index) => (
              <tr key={index}>
                <td>{row.label}</td>
                <td>{row.value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default App;