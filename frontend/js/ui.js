document.getElementById('btn-upload').onclick = () => {
    document.getElementById('upload-modal').classList.remove('hidden');
};

document.getElementById('cancel-upload').onclick = () => {
    document.getElementById('upload-modal').classList.add('hidden');
};

document.getElementById('close-panel').onclick = () => {
    document.getElementById('details-panel').classList.add('hidden');
};

document.getElementById('upload-form').onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('name', document.getElementById('node-name').value);
    formData.append('node_type', document.getElementById('node-type-select').value);
    
    const file = document.getElementById('file-input').files[0];
    if (file) formData.append('file', file);
    
    formData.append('raw_value', document.getElementById('raw-value').value);
    
    const tags = document.getElementById('node-tags').value.split(',').map(t => t.trim());
    formData.append('tags', JSON.stringify(tags));

    try {
        await api.createNode(formData);
        document.getElementById('upload-modal').classList.add('hidden');
        refreshGraph();
        e.target.reset();
    } catch (err) {
        alert("Erro ao criar nó: " + err.message);
    }
};

document.getElementById('search-input').oninput = async (e) => {
    const q = e.target.value;
    if (q.length > 2) {
        const results = await api.search(q);
        highlightNodes(results.map(n => n.id));
    } else {
        highlightNodes([]);
    }
};

