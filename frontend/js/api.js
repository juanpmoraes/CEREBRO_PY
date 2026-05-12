const API_URL = 'http://localhost:8000';

const api = {
    async getGraph() {
        const response = await fetch(`${API_URL}/graph`);
        return response.json();
    },

    async createNode(formData) {
        const response = await fetch(`${API_URL}/nodes`, {
            method: 'POST',
            body: formData
        });
        return response.json();
    },

    async getNode(id) {
        const response = await fetch(`${API_URL}/nodes/${id}`);
        return response.json();
    },

    async search(query) {
        const response = await fetch(`${API_URL}/search?q=${query}`);
        return response.json();
    },

    async createEdge(sourceId, targetId, relationship = 'related_to') {
        const response = await fetch(`${API_URL}/edges`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source_id: sourceId, target_id: targetId, relationship })
        });
        return response.json();
    }
};
