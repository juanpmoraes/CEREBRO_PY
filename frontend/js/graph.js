let graph;
let highlightedNodes = new Set();

function initGraph() {
    graph = ForceGraph()(document.getElementById('graph-container'))
        .nodeId('id')
        .nodeLabel('name')
        .nodeColor(node => highlightedNodes.has(node.id) ? '#ff0000' : null)
        .nodeCanvasObject((node, ctx, globalScale) => {
            const label = node.name;
            const fontSize = 12/globalScale;
            ctx.font = `${fontSize}px Inter`;
            const textWidth = ctx.measureText(label).width;
            const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2); // some padding

            ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
            ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);

            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = highlightedNodes.has(node.id) ? '#ff4444' : '#333';
            ctx.fillText(label, node.x, node.y);

            node.__bckgDimensions = bckgDimensions; // to re-use in nodePointerAreaPaint
        })
        .nodePointerAreaPaint((node, color, ctx) => {
            ctx.fillStyle = color;
            const bckgDimensions = node.__bckgDimensions;
            bckgDimensions && ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);
        })
        .linkSource('source_id')

        .linkTarget('target_id')
        .onNodeClick(node => {
            showDetails(node.id);
        })
        .linkDirectionalParticles(2)
        .linkDirectionalParticleSpeed(d => d.weight * 0.01);

    refreshGraph();
    connectWS();
}

function connectWS() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
    ws.onmessage = (event) => {

        const data = JSON.parse(event.data);
        if (data.type === "node_created") {
            console.log("Novo nó criado:", data.name);
            refreshGraph();
        }
    };
    ws.onclose = () => {
        setTimeout(connectWS, 3000); // Tentar reconectar
    };
}


async function refreshGraph() {
    try {
        const data = await api.getGraph();
        graph.graphData(data);
    } catch (err) {
        console.error("Erro ao carregar grafo:", err);
    }
}

async function showDetails(nodeId) {
    const node = await api.getNode(nodeId);
    document.getElementById('node-title').innerText = node.name;
    document.getElementById('node-type').innerText = node.node_type;
    document.getElementById('node-mime').innerText = node.mime_type || 'N/A';
    document.getElementById('node-summary').innerText = node.summary || 'Sem resumo disponível.';
    
    document.getElementById('details-panel').classList.remove('hidden');
}

function highlightNodes(nodeIds) {
    highlightedNodes = new Set(nodeIds);
    graph.nodeColor(graph.nodeColor()); // Force repaint
}


// Inicializar quando o DOM carregar
document.addEventListener('DOMContentLoaded', initGraph);
