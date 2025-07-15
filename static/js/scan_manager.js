document.addEventListener("DOMContentLoaded", () => {

  // Inicializa DataTable y guarda instancia global
  const scansTable = $('#scans-table').DataTable({
    columns: [
      { title: "Fecha" },
      { title: "ID" },
      { title: "Nombre" },
      { title: "Dominio / IP" },
      { title: "Descripción" },
      { title: "Módulos" },
      { title: "Agresividad" },
      { title: "Estado" },
      { title: "Progreso" },
      { title: "Acciones", orderable: false, searchable: false }
    ],
    language: {
      url: "//cdn.datatables.net/plug-ins/1.13.4/i18n/es-ES.json"
    },
    order: [[0, 'desc']],
    deferRender: true,
    searching: true,
    paging: true,
    lengthChange: true,
  });

  // Renderiza los globitos con color para el flujo (módulos/scripts)
function renderModulesGlobitos(flow) {
  if (!Array.isArray(flow) || flow.length === 0) return '';

  return flow.map((item, idx) => {
    let color = '#6c757d'; // fallback
    if (item.type === 'mod' && window.modules_info && window.modules_info[item.name]) {
      color = window.modules_info[item.name].icon_color || color;
    } else if (item.type === 'script' && window.scripts_info && window.scripts_info[item.name]) {
      color = window.scripts_info[item.name].icon_color || color;
    }

    const arrow = idx < flow.length - 1 ? `<span class="mx-1">&rarr;</span>` : '';
    return `<span class="badge rounded-pill" style="background-color: ${color};">${item.name}</span>${arrow}`;
  }).join('');
}

  // Botones acción por escaneo
/*function renderActionButtons(scan) {
  if (!scan || !scan.id) return '';

  const flowJson = JSON.stringify(scan.flow || []).replace(/"/g, '&quot;');
  const scanId = scan.id;
  const folderName = scan.folder_name || '';

  return `
    <button class="btn btn-sm btn-success me-1" onclick="startScan('${scanId}', JSON.parse('${flowJson}'))">Start</button>
    <button class="btn btn-sm btn-warning me-1" onclick="pauseScan('${scanId}')">Pause</button>
    <button class="btn btn-sm btn-danger me-1" onclick="deleteScan('${scanId}', '${folderName}')">Eliminar</button>
    <button class="btn btn-sm btn-info" onclick="showReport('${scanId}')">Report</button>
  `;
}*/

/*
V2
function renderActionButtons(scan) {
  if (!scan || !scan.id) return '';

  const scanId = scan.id;
  const flowJson = JSON.stringify(scan.flow || []).replace(/"/g, '&quot;');
  const folderName = scan.folder_name || '';

  return `
    <button class="btn btn-outline-success btn-sm me-1" title="Iniciar" onclick="startScan('${scanId}', JSON.parse('${flowJson}'))">
      <i class="bi bi-play-fill"></i>
    </button>
    <button class="btn btn-outline-warning btn-sm me-1" title="Pausar" onclick="pauseScan('${scanId}')">
      <i class="bi bi-pause-fill"></i>
    </button>
    <button class="btn btn-outline-danger btn-sm me-1" title="Eliminar" onclick="deleteScan('${scanId}', '${folderName}')">
      <i class="bi bi-trash-fill"></i>
    </button>
    <button class="btn btn-outline-info btn-sm" title="Ver Reporte" onclick="showReport('${scanId}')">
      <i class="bi bi-file-earmark-text-fill"></i>
    </button>
  `;
}
*/
function renderActionButtons(scan) {
  const scanId = scan.id;
  const folderName = scan.folder_name;
  const flow = scan.flow || [];
  const flowJson = JSON.stringify(flow).replace(/"/g, '&quot;');

  return `
    <div class="d-flex flex-row flex-nowrap gap-1">
      <button class="btn btn-success btn-sm p-1"
              data-bs-toggle="tooltip"
              title="Iniciar" onclick="startScan('${scanId}', JSON.parse('${flowJson}'))">
        <i class="bi bi-play-fill"></i>
      </button>
      <button class="btn btn-warning btn-sm p-1" data-bs-toggle="tooltip" title="Pausar" onclick="pauseScan('${scanId}')">
        <i class="bi bi-pause-fill"></i>
      </button>
      <button class="btn btn-secondary btn-sm p-1" data-bs-toggle="tooltip" title="Detener" onclick="stopScan('${scanId}')">
        <i class="bi bi-stop-fill"></i>
      </button>
      <button class="btn btn-info btn-sm p-1 text-white" data-bs-toggle="tooltip" title="Informe" onclick="showReport('${scanId}')">
        <i class="bi bi-file-earmark-text-fill"></i>
      </button>
      <button class="btn btn-danger btn-sm p-1" data-bs-toggle="tooltip" title="Eliminar" onclick="deleteScan('${scanId}', '${folderName}')">
        <i class="bi bi-trash-fill"></i>
      </button>
    </div>
  `;
}




  // Renderiza la barra de progreso
  function renderProgressBar(percentage) {
    let pct = typeof percentage === 'number' && !isNaN(percentage) ? percentage : 0;
    pct = Math.max(0, Math.min(100, pct));
    const barClass = pct >= 100 ? 'bg-success' : 'bg-primary';
    const style = pct === 0 ? 'background-color: transparent;' : '';
    return `
      <div class="progress" style="height: 20px; position: relative; background-color: #e9ecef;">
        <div class="progress-bar ${barClass}" role="progressbar" style="width: ${pct}%; ${style}" aria-valuenow="${pct}" aria-valuemin="0" aria-valuemax="100"></div>
        <span style="position: absolute; top: 0; left: 50%; transform: translateX(-50%); height: 100%; display: flex; align-items: center; color: #000; font-weight: 600; text-shadow: 0 0 3px rgba(255,255,255,0.8);">
          ${pct}%
        </span>
      </div>`;
  }

  // Renderiza badge de agresividad
  function renderAggressivenessBadge(value) {
    const levels = {
      0: { label: "Muy Baja (paranoid)", color: "#6c757d" },
      2: { label: "Baja (sneaky)", color: "#0dcaf0" },
      4: { label: "Moderado (polite)", color: "#198754" },
      6: { label: "Normal (normal)", color: "#ffc107" },
      8: { label: "Alta (aggressive)", color: "#fd7e14" },
      10: { label: "Muy Alta (insane)", color: "#dc3545" }
    };
    const nearest = Object.keys(levels)
      .map(Number)
      .reduce((prev, curr) => Math.abs(curr - value) < Math.abs(prev - value) ? curr : prev);
    const level = levels[nearest] || { label: 'Desconocido', color: '#6c757d' };

    return `
      <span class="badge rounded-pill" style="background-color: ${level.color}; cursor: default;" title="${level.label}">
        ${value} - ${level.label}
      </span>`;
  }




  // Funciones expuestas para botones
  window.startScan = async (id, flow) => {
    if (!Array.isArray(flow) || flow.length === 0) {
      alert('No hay módulos o scripts seleccionados para ejecutar');
      return;
    }
    try {
      await axios.post(`/api/scans/${id}/start`, { modules: flow });
      fetchScans();
    } catch (e) {
      console.error('Error iniciando escaneo:', e);
      alert('Error iniciando escaneo');
    }
  };


  window.pauseScan = async (id) => {
    try {
      await axios.post(`/api/scans/${id}/pause`);
      fetchScans();
    } catch (e) {
      console.error('Error pausando escaneo:', e);
    }
  };

  window.stopScan = async (id) => {
    try {
      await axios.post(`/api/scans/${id}/stop`);
      fetchScans();
    } catch (e) {
      console.error('Error deteniendo escaneo:', e);
    }
  };

  window.deleteScan = async (scanId, folderName) => {
    if (!confirm(`¿Seguro que quieres eliminar el escaneo "${folderName}"?`)) return;
    try {
      const response = await axios.delete(`/api/scans/${scanId}`);
      alert(response.data.message || 'Escaneo eliminado');
      fetchScans();
    } catch (e) {
      console.error('Error eliminando escaneo:', e);
      alert('Error al eliminar el escaneo');
    }
  };
  window.showReport = (id) => {
    window.open(`/report/${id}`, '_blank');
  };

  // Fetch y carga los escaneos en la tabla
  async function fetchScans() {
    try {
      const res = await axios.get('/api/scans');
      const scans = res.data.scans || [];

      scansTable.clear();

      if (scans.length === 0) {
        scansTable.draw();
        return;
      }

      scans.forEach(scan => {
        // Formatea fecha para ordenar y mostrar
        const createdAt = scan.created_at ? new Date(scan.created_at) : new Date();
        const createdAtStr = createdAt.toLocaleString('es-ES', {
          year: 'numeric', month: '2-digit', day: '2-digit',
          hour: '2-digit', minute: '2-digit', second: '2-digit'
        });

        scansTable.row.add([
          `<span data-order="${scan.created_at}">${createdAtStr}</span>`,
          scan.id || '',
          scan.name || '',
          scan.target || '',
          scan.description || '',
          renderModulesGlobitos(scan.flow),
          renderAggressivenessBadge(scan.aggressiveness || 0),
          `<span class="text-capitalize">${scan.status || ''}</span>`,
          renderProgressBar(scan.progress || 0),
          renderActionButtons(scan)
        ]);
      });
//renderActionButtons(scan.id, scan.folder_name, scan.flow)
      scansTable.draw();

    } catch (err) {
      console.error('Error cargando escaneos:', err);
    }
  }

  // Carga inicial y refresco cada 10s
  fetchScans();
  setInterval(fetchScans, 10000);


  // === Código que compartiste para añadir elementos al flow (puedes ajustar según tu HTML) ===

  // Aquí asumo que btn y flowContainer ya están definidos en tu contexto.
  // Si no, deberías declarar, por ejemplo:
  // const flowContainer = document.getElementById('flow-container');
  // const btn = document.querySelector('.your-btn-selector');

  // El bloque original de añadir elementos y flechas queda intacto, sólo ajustado en estilo y event listener.

  // ... (tu código para gestión flow) ...

  // === Slider agresividad (igual que lo tienes) ===
  const slider = document.getElementById('aggressiveness');
  const aggrVal = document.getElementById('aggr_val');
  const aggrText = document.getElementById('aggr_text');

  function updateSliderVisual() {
    if (!slider || !aggrVal || !aggrText) return;

    const val = parseInt(slider.value, 10);
    const percent = ((val - slider.min) / (slider.max - slider.min)) * 100;
    slider.style.background = `linear-gradient(to right, #0d6efd 0%, #0d6efd ${percent}%, #dee2e6 ${percent}%, #dee2e6 100%)`;
    aggrVal.textContent = val;

    const levels = {
      0: { label: "Muy Baja (paranoid)", color: "#6c757d" },
      2: { label: "Baja (sneaky)", color: "#0dcaf0" },
      4: { label: "Moderado (polite)", color: "#198754" },
      6: { label: "Normal (normal)", color: "#ffc107" },
      8: { label: "Alta (aggressive)", color: "#fd7e14" },
      10: { label: "Muy Alta (insane)", color: "#dc3545" }
    };

    const closest = Object.keys(levels)
      .map(Number)
      .reduce((prev, curr) => Math.abs(curr - val) < Math.abs(prev - val) ? curr : prev);

    const level = levels[closest];
    aggrText.textContent = level.label;
    aggrText.style.backgroundColor = level.color;
    aggrText.style.color = "#fff";
    aggrText.style.padding = "0.2em 0.6em";
    aggrText.style.borderRadius = "0.3em";
  }

  if (slider) {
    slider.addEventListener('input', updateSliderVisual);
    updateSliderVisual();
  }

});
