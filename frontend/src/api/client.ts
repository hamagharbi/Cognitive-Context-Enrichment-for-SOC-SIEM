import axios from 'axios';

const client = axios.create({
  baseURL: '/api', // Proxied by Vite to http://localhost:8000
  headers: {
    'Content-Type': 'application/json',
  },
});

export default client;
