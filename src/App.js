import React, { useEffect, useState, useRef } from 'react';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { PolarArea, Bar } from 'react-chartjs-2';
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
  PointElement,
} from 'chart.js';
import './CraterScene.css';
import './App.css';

// Register Chart.js components
ChartJS.register(RadialLinearScale, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement);

const App = () => {
  const containerRef = useRef(null);
  const bannerRef = useRef(null);
  const [error, setError] = useState(null);
  const [diameterChartData, setDiameterChartData] = useState(null);
  const [depthChartData, setDepthChartData] = useState(null);
  const [barChartData, setBarChartData] = useState(null);
  const [comparisonChartData, setComparisonChartData] = useState(null);
  const [tableData, setTableData] = useState([]);

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
      '/images/banner.jpg',
      (texture) => {
        scene.background = texture;
      },
      undefined,
      (err) => {
        setError('Failed to load background texture');
        console.error('Texture load error:', err);
      }
    );

    const light = new THREE.HemisphereLight(0xffffff, 0x444444);
    light.position.set(0, 1, 0);
    scene.add(light);

    // Load BB-8 Model
    const loader = new GLTFLoader();
    loader.load(
      '/models/bb8_animated.glb',
      (gltf) => {
        const bb8 = gltf.scene;
        bb8.position.set(-5, 0, 0);
        bb8.scale.set(4, 4, 4);
        scene.add(bb8);

        gsap.to(bb8.position, {
          x: 5,
          duration: 10,
          ease: 'power1.inOut',
          repeat: -1,
          yoyo: true,
        });
      },
      undefined,
      (error) => {
        setError('Failed to load BB-8 model');
        console.error('Model load error:', error);
      }
    );

    let animationFrameId;
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      renderer.render(scene, camera);
    };
    animate();

    // Crater statistics
    const yourStats = {
      total_craters: 1047,
      mean_diameter_km: 1.7156024707291615,
      median_diameter_km: 1.54715556557901,
      min_diameter_km: 1.034176589165282,
      max_diameter_km: 4.173477802981229,
      mean_depth_km: 1.2845983951575932,
      median_depth_km: 1.1392157,
      min_depth_km: 0.0,
      max_depth_km: 3.5
    };

    const scientificMeanDiameterKm = 6.8;

    try {
      // Set table data
      setTableData([
        { label: 'Mean Diameter (km)', value: yourStats.mean_diameter_km },
        { label: 'Median Diameter (km)', value: yourStats.median_diameter_km },
        { label: 'Min Diameter (km)', value: yourStats.min_diameter_km },
        { label: 'Max Diameter (km)', value: yourStats.max_diameter_km },
        { label: 'Mean Depth (km)', value: yourStats.mean_depth_km },
        { label: 'Median Depth (km)', value: yourStats.median_depth_km },
        { label: 'Min Depth (km)', value: yourStats.min_depth_km },
        { label: 'Max Depth (km)', value: yourStats.max_depth_km },
      ]);

      // Chart data setup
      setDiameterChartData({
        labels: ['Mean Diameter (km)', 'Median Diameter (km)', 'Min Diameter (km)', 'Max Diameter (km)'],
        datasets: [{
          label: 'Diameter (km)',
          data: [yourStats.mean_diameter_km, yourStats.median_diameter_km, yourStats.min_diameter_km, yourStats.max_diameter_km],
          backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)', 'rgba(75, 192, 192, 0.2)'],
          borderColor: ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)', 'rgba(75, 192, 192, 1)'],
          borderWidth: 1,
        }],
      });

      setDepthChartData({
        labels: ['Mean Depth (km)', 'Median Depth (km)', 'Min Depth (km)', 'Max Depth (km)'],
        datasets: [{
          label: 'Depth (km)',
          data: [yourStats.mean_depth_km, yourStats.median_depth_km, yourStats.min_depth_km, yourStats.max_depth_km],
          backgroundColor: ['rgba(153, 102, 255, 0.2)', 'rgba(255, 159, 64, 0.2)', 'rgba(75, 192, 192, 0.2)', 'rgba(255, 99, 132, 0.2)'],
          borderColor: ['rgba(153, 102, 255, 1)', 'rgba(255, 159, 64, 1)', 'rgba(75, 192, 192, 1)', 'rgba(255, 99, 132, 1)'],
          borderWidth: 1,
        }],
      });

      setBarChartData({
        labels: ['Mean Diameter (km)', 'Median Diameter (km)', 'Min Diameter (km)', 'Max Diameter (km)', 'Mean Depth (km)', 'Median Depth (km)', 'Min Depth (km)', 'Max Depth (km)'],
        datasets: [{
          label: 'Statistics',
          data: [yourStats.mean_diameter_km, yourStats.median_diameter_km, yourStats.min_diameter_km, yourStats.max_diameter_km, yourStats.mean_depth_km, yourStats.median_depth_km, yourStats.min_depth_km, yourStats.max_depth_km],
          backgroundColor: 'rgba(0, 255, 255, 0.2)',
          borderColor: 'rgba(0, 255, 255, 1)',
          borderWidth: 1,
        }],
      });

      setComparisonChartData({
        labels: ['Your Mean Diameter (km)', 'Scientific Mean Diameter (km)'],
        datasets: [{
          label: 'Diameter Comparison',
          data: [yourStats.mean_diameter_km, scientificMeanDiameterKm],
          backgroundColor: ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)'],
          borderColor: ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)'],
          borderWidth: 1,
        }],
      });
    } catch (err) {
      setError('Failed to process chart data');
      console.error('Chart data error:', err);
    }

    // Cleanup
    return () => {
      cancelAnimationFrame(animationFrameId);
      renderer.dispose();
    };
  }, []);

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top', labels: { color: '#FFD700' } },
      tooltip: { backgroundColor: 'rgba(139, 69, 19, 0.8)', titleColor: '#FFD700', bodyColor: '#FFD700' },
    },
    scales: {
      r: {
        angleLines: { color: 'rgba(255, 215, 0, 0.2)' },
        grid: { color: 'rgba(255, 215, 0, 0.2)' },
        pointLabels: { color: '#FFD700', font: { size: 18 } },
        ticks: { font: { size: 16 } },
      },
    },
    maintainAspectRatio: false,
  };

  const barChartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top', labels: { color: '#FFD700' } },
      tooltip: { backgroundColor: 'rgba(139, 69, 19, 0.8)', titleColor: '#FFD700', bodyColor: '#FFD700' },
    },
    scales: {
      x: { ticks: { color: '#FFD700', font: { size: 16 } }, grid: { color: 'rgba(255, 215, 0, 0.2)' } },
      y: { ticks: { color: '#FFD700', font: { size: 16 } }, grid: { color: 'rgba(255, 215, 0, 0.2)' } },
    },
    maintainAspectRatio: false,
  };

  const comparisonChartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top', labels: { color: '#FFD700' } },
      tooltip: { backgroundColor: 'rgba(139, 69, 19, 0.8)', titleColor: '#FFD700', bodyColor: '#FFD700' },
    },
    scales: {
      x: { ticks: { color: '#FFD700', font: { size: 16 } }, grid: { color: 'rgba(255, 215, 0, 0.2)' } },
      y: { ticks: { color: '#FFD700', font: { size: 16 } }, grid: { color: 'rgba(255, 215, 0, 0.2)' } },
    },
    maintainAspectRatio: false,
  };

  return (
    <div ref={containerRef} className="crater-scene-container">
      <div ref={bannerRef} className="banner" style={{ backgroundImage: "url('/images/banner.jpg')", backgroundSize: "contain" }}>
        <div className="title-overlay"></div>
      </div>
      <div className="link-container">
        <button onClick={() => window.location.href='https://github.com/tmcwilliam707/mars-crater-studio'}>Link to Dataset</button>
      </div>
      <div className="small-title"></div>
      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}
      {diameterChartData && depthChartData && barChartData && comparisonChartData ? (
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
          <div className="chart-container">
            <Bar data={comparisonChartData} options={comparisonChartOptions} />
          </div>
        </div>
      ) : !error && (
        <div className="loading-message">
          Loading crater data...
        </div>
      )}
      <div className="content" style={{ backgroundImage: "url('/images/starry.jpg')" }}>
        <p className="welcome-text">Explore the fascinating world of Mars craters with detailed statistics and visualizations.</p>
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
      <div className="additional-info">
        <h3>Mapping to Mars Regions</h3>
        <p>### lat-30_lon060.pgm (-30° to 0°, 60°E to 120°E)</p>
        <ul>
          <li><strong>Region</strong>: Spans parts of Arabia Terra (northern) and Terra Sabaea (southern).</li>
          <li><strong>Description</strong>: Arabia Terra is a heavily cratered highland in the northern hemisphere, transitioning to Terra Sabaea’s rugged terrain in the south. Includes features like Schiaparelli Crater (~460 km diameter, ~2°S, 17°E, just west of the tile).</li>
          <li><strong>Label</strong>: "Arabia Terra - Terra Sabaea".</li>
        </ul>
        <p>### lat30_lon000.pgm (30°N to 60°N, 0°E to 60°E)</p>
        <ul>
          <li><strong>Region</strong>: Covers parts of Acidalia Planitia (lower) and Utopia Planitia (upper).</li>
          <li><strong>Description</strong>: Acidalia Planitia is a vast northern plain with fewer craters, while Utopia Planitia (site of Viking 2 landing) has moderate cratering and volcanic features.</li>
          <li><strong>Label</strong>: "Acidalia Planitia - Utopia Planitia".</li>
        </ul>
        <p>### lat30_lon300.pgm (30°N to 60°N, 300°E to 360°E)</p>
        <ul>
          <li><strong>Region</strong>: Encompasses parts of Arcadia Planitia and Tharsis Montes (western edge).</li>
          <li><strong>Description</strong>: Arcadia Planitia is a smooth northern plain with some craters, adjacent to the Tharsis volcanic region (e.g., Alba Mons near 40°N, 250°E, just outside).</li>
          <li><strong>Label</strong>: "Arcadia Planitia - Tharsis Border".</li>
        </ul>
      </div>
      <div className="image-container centered">
        <img src="/themis_lat30_lon300_detection-2.png" alt="Mars crater detection" style={{ display: 'block', margin: '0 auto' }} />
      </div>
      <div className="mosaic-container centered">
        <img src="hirise_submosaic_0.png" alt="Mars mosaic" style={{ width: '50%', height: 'auto', display: 'block', margin: '0 auto' }} />
      </div>
      <div className="additional-info" style={{ textAlign: 'center' }}>
        <h3>Process Explanation</h3>
        <p>We converted grayscale images (PGM - Themis) to kilometers using a specific conversion factor derived from the THEMIS data. Edge detection algorithms, such as Canny edge detection, were used to identify the boundaries of craters. This project depends on assumption approximate of max crater depth of 8km and max width of 7000 k to derive sampling alogritm using canny detection with sigma=1, This process involves several steps, including noise reduction, gradient calculation, non-maximum suppression, and edge tracking by hysteresis.</p>
        <p>We encourage you to download the PGM files and try these experiments yourself. You can find the PGM files in the dataset linked above. Experiment with different edge detection algorithms and conversion factors to see how they affect the results.</p>
      </div>
      <div className="footer" style={{ textAlign: 'center' }}>
        <p>© MARS CRATER STUDIO 2025</p>
      </div>
    </div>
  );
};

export default App;