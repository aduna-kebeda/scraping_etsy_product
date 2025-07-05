import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function App() {
  const [products, setProducts] = useState([]);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    axios.get('http://localhost:5000/api/products')
      .then(response => setProducts(response.data))
      .catch(error => console.error('Error fetching products:', error));
  }, []);

  const filteredProducts = products.filter(p => p.name && p.name.toLowerCase().includes(filter.toLowerCase()));

  const chartData = {
    labels: ['0-20', '20-50', '50-100', '100+'],
    datasets: [{
      label: 'Price Distribution',
      data: [
        products.filter(p => p.price <= 20).length,
        products.filter(p => p.price > 20 && p.price <= 50).length,
        products.filter(p => p.price > 50 && p.price <= 100).length,
        products.filter(p => p.price > 100).length
      ],
      backgroundColor: 'rgba(75, 192, 192, 0.6)'
    }]
  };

  return (
    <div style={{ padding: 24, fontFamily: 'Arial, sans-serif' }}>
      <h1>Etsy Vintage Jewelry Dashboard</h1>
      <input
        type="text"
        placeholder="Filter by product name"
        value={filter}
        onChange={e => setFilter(e.target.value)}
        style={{ marginBottom: 16, padding: 8, width: 300 }}
      />
      <Bar data={chartData} options={{ responsive: true, plugins: { title: { display: true, text: 'Price Distribution' } } }} />
      <table style={{ width: '100%', marginTop: 24, borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ border: '1px solid #ccc', padding: 8 }}>Name</th>
            <th style={{ border: '1px solid #ccc', padding: 8 }}>Price ($)</th>
            <th style={{ border: '1px solid #ccc', padding: 8 }}>Seller</th>
            <th style={{ border: '1px solid #ccc', padding: 8 }}>Rating</th>
            <th style={{ border: '1px solid #ccc', padding: 8 }}>Brand</th>
            <th style={{ border: '1px solid #ccc', padding: 8 }}>URL</th>
          </tr>
        </thead>
        <tbody>
          {filteredProducts.map((product, index) => (
            <tr key={index}>
              <td style={{ border: '1px solid #ccc', padding: 8 }}>{product.name}</td>
              <td style={{ border: '1px solid #ccc', padding: 8 }}>{product.price}</td>
              <td style={{ border: '1px solid #ccc', padding: 8 }}>{product.seller}</td>
              <td style={{ border: '1px solid #ccc', padding: 8 }}>{product.rating}</td>
              <td style={{ border: '1px solid #ccc', padding: 8 }}>{product.brand}</td>
              <td style={{ border: '1px solid #ccc', padding: 8 }}>
                {product.url ? <a href={product.url} target="_blank" rel="noopener noreferrer">View</a> : ''}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
