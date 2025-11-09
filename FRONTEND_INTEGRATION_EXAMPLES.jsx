// ============================================================================
// EJEMPLOS DE USO EN FRONTEND REACT
// ============================================================================
// Este archivo contiene ejemplos de cómo integrar los nuevos endpoints
// en componentes React con Axios

import axios from 'axios';
import { useEffect, useState } from 'react';

const API_BASE = 'http://127.0.0.1:8002/api';

// ============================================================================
// 1. Hook personalizado para obtener datos de la API
// ============================================================================

/**
 * Hook para fetchear datos de estadísticas con manejo de errores
 */
function useStatsData(endpoint, params = {}) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const queryString = new URLSearchParams(params).toString();
        const url = `${API_BASE}${endpoint}${queryString ? '?' + queryString : ''}`;
        const response = await axios.get(url);
        setData(response.data);
        setError(null);
      } catch (err) {
        setError(err.message);
        setData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [endpoint, params]);

  return { data, loading, error };
}

// ============================================================================
// 2. COMPONENTE: Gráfico de Barras por Vía
// ============================================================================

/**
 * Visualiza las Top 20 vías con más siniestros usando Recharts
 */
function GraficoVias({ year = 2024 }) {
  const { data, loading, error } = useStatsData('/siniestros/por_via/', { year });

  if (loading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Siniestros por Vía ({year})</h2>
      {/* Aquí irá un BarChart de recharts */}
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}

// Ejemplo con Recharts (requiere: npm install recharts):
/*
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

function GraficoViasConRecharts({ year = 2024 }) {
  const { data } = useStatsData('/siniestros/por_via/', { year });

  return (
    <BarChart width={800} height={400} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="via" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Bar dataKey="total_siniestros" fill="#8884d8" />
      <Bar dataKey="total_lesionados" fill="#82ca9d" />
      <Bar dataKey="total_fallecidos" fill="#ffc658" />
    </BarChart>
  );
}
*/

// ============================================================================
// 3. COMPONENTE: Tabla de Causas Probables
// ============================================================================

/**
 * Visualiza las causas de siniestros en una tabla con sort/filter
 */
function TablaCausas({ year = 2024 }) {
  const { data, loading, error } = useStatsData('/siniestros/por_causa_probable/', { year });
  const [sortBy, setSortBy] = useState('total_siniestros');
  const [sortOrder, setSortOrder] = useState('desc');

  const sortedData = [...data].sort((a, b) => {
    const aVal = a[sortBy] || 0;
    const bVal = b[sortBy] || 0;
    return sortOrder === 'desc' ? bVal - aVal : aVal - bVal;
  });

  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };

  if (loading) return <div>Cargando tabla...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Causas de Siniestros ({year})</h2>
      <table style={{ borderCollapse: 'collapse', width: '100%' }}>
        <thead>
          <tr style={{ backgroundColor: '#f0f0f0' }}>
            <th onClick={() => handleSort('causa')} style={{ cursor: 'pointer', padding: '10px' }}>
              Causa {sortBy === 'causa' && (sortOrder === 'desc' ? '↓' : '↑')}
            </th>
            <th onClick={() => handleSort('total_siniestros')} style={{ cursor: 'pointer', padding: '10px' }}>
              Siniestros {sortBy === 'total_siniestros' && (sortOrder === 'desc' ? '↓' : '↑')}
            </th>
            <th onClick={() => handleSort('total_lesionados')} style={{ cursor: 'pointer', padding: '10px' }}>
              Lesionados {sortBy === 'total_lesionados' && (sortOrder === 'desc' ? '↓' : '↑')}
            </th>
            <th onClick={() => handleSort('total_fallecidos')} style={{ cursor: 'pointer', padding: '10px' }}>
              Fallecidos {sortBy === 'total_fallecidos' && (sortOrder === 'desc' ? '↓' : '↑')}
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedData.map((causa) => (
            <tr key={causa.id} style={{ borderBottom: '1px solid #ddd' }}>
              <td style={{ padding: '10px' }}>{causa.causa}</td>
              <td style={{ padding: '10px', textAlign: 'center' }}>{causa.total_siniestros}</td>
              <td style={{ padding: '10px', textAlign: 'center' }}>{causa.total_lesionados}</td>
              <td style={{ padding: '10px', textAlign: 'center' }}>{causa.total_fallecidos}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ============================================================================
// 4. COMPONENTE: Gráfico de Línea - Evolución Anual
// ============================================================================

/**
 * Visualiza la evolución anual de siniestros con LineChart de Recharts
 */
function GraficoEvolucionAnual() {
  const { data, loading, error } = useStatsData('/siniestros/evolucion_anual/', {});

  if (loading) return <div>Cargando gráfico anual...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Evolución Anual de Siniestros</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}

/*
// Con Recharts:
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

function GraficoEvolucionAnualConRecharts() {
  const { data } = useStatsData('/siniestros/evolucion_anual/', {});

  return (
    <LineChart width={800} height={400} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="ano" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Line type="monotone" dataKey="total_siniestros" stroke="#8884d8" />
      <Line type="monotone" dataKey="total_lesionados" stroke="#82ca9d" />
      <Line type="monotone" dataKey="total_fallecidos" stroke="#ffc658" />
    </LineChart>
  );
}
*/

// ============================================================================
// 5. COMPONENTE: KPIs con Datos de Evolución Anual
// ============================================================================

/**
 * Muestra KPIs calculados a partir de la evolución anual
 */
function KPIsEvolucion() {
  const { data, loading, error } = useStatsData('/siniestros/evolucion_anual/', {});

  if (loading) return <div>Cargando KPIs...</div>;
  if (error) return <div>Error: {error}</div>;

  // Obtener último y penúltimo año
  const current = data[data.length - 1];
  const previous = data[data.length - 2];

  const cambioSiniestros = current && previous ? 
    ((current.total_siniestros - previous.total_siniestros) / previous.total_siniestros * 100).toFixed(1) 
    : 0;

  const cambioLesionados = current && previous ?
    ((current.total_lesionados - previous.total_lesionados) / previous.total_lesionados * 100).toFixed(1)
    : 0;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
      <div style={{ padding: '20px', backgroundColor: '#f0f0f0', borderRadius: '8px' }}>
        <h3>Siniestros {current?.ano}</h3>
        <p style={{ fontSize: '24px', fontWeight: 'bold' }}>{current?.total_siniestros}</p>
        <p style={{ color: cambioSiniestros > 0 ? 'red' : 'green' }}>
          {cambioSiniestros > 0 ? '+' : ''}{cambioSiniestros}% vs {previous?.ano}
        </p>
      </div>

      <div style={{ padding: '20px', backgroundColor: '#f0f0f0', borderRadius: '8px' }}>
        <h3>Lesionados {current?.ano}</h3>
        <p style={{ fontSize: '24px', fontWeight: 'bold' }}>{current?.total_lesionados}</p>
        <p style={{ color: cambioLesionados > 0 ? 'red' : 'green' }}>
          {cambioLesionados > 0 ? '+' : ''}{cambioLesionados}% vs {previous?.ano}
        </p>
      </div>

      <div style={{ padding: '20px', backgroundColor: '#f0f0f0', borderRadius: '8px' }}>
        <h3>Fallecidos {current?.ano}</h3>
        <p style={{ fontSize: '24px', fontWeight: 'bold' }}>{current?.total_fallecidos}</p>
      </div>
    </div>
  );
}

// ============================================================================
// 6. COMPONENTE PRINCIPAL: Dashboard
// ============================================================================

/**
 * Dashboard que integra todos los componentes
 */
export function Dashboard() {
  const [year, setYear] = useState(2024);

  return (
    <div style={{ padding: '20px' }}>
      <h1>📊 Dashboard de Siniestros</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <label>
          Año: 
          <input 
            type="number" 
            value={year} 
            onChange={(e) => setYear(parseInt(e.target.value))}
            style={{ marginLeft: '10px', padding: '5px' }}
          />
        </label>
      </div>

      <section style={{ marginBottom: '40px' }}>
        <GraficoVias year={year} />
      </section>

      <section style={{ marginBottom: '40px' }}>
        <TablaCausas year={year} />
      </section>

      <section style={{ marginBottom: '40px' }}>
        <GraficoEvolucionAnual />
      </section>

      <section>
        <KPIsEvolucion />
      </section>
    </div>
  );
}

// ============================================================================
// NOTAS IMPORTANTES
// ============================================================================

/*
1. INSTALACIONES NECESARIAS:
   npm install axios
   npm install recharts  (para gráficos)

2. VARIABLES DE ENTORNO:
   - Ajusta API_BASE según donde esté corriendo Django
   - Para desarrollo: http://127.0.0.1:8002/api
   - Para producción: tu_dominio.com/api

3. CORS:
   - Ya está configurado en Django settings.py
   - Asegúrate que el frontend está en CORS_ALLOWED_ORIGINS

4. CACHING:
   - Los endpoints tienen caching en el servidor (5 min y 1 hora)
   - Para desarrollo, puedes desactivar el caching comentando @method_decorator

5. ERROR HANDLING:
   - El hook useStatsData maneja errores automáticamente
   - Considera agregar reintentos automáticos en caso de fallo

6. PERFORMANCE:
   - Usa React.memo para evitar re-renders innecesarios
   - Considera usar useCallback para funciones en hooks
   - Lazy load componentes pesados con React.lazy
*/
