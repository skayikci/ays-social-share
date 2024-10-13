const API_BASE_URL = '/api';

export const getGroupedPosts = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/posts/grouped`);
        const data = await response.json();
        if (response.ok) {
            return data;
        } else {
            console.error('Failed to fetch grouped posts:', data.message);
        }
    } catch (error) {
        console.error("Error fetching grouped posts:", error);
    }
};

export const generatePosts = async (prompt) => {
    const response = await fetch(`${API_BASE_URL}/posts/generate_posts`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
    });
    if (!response.ok) {
        throw new Error(`Error generating posts: ${response.statusText}`);
    }
    return await response.json();
};

export const approvePost = async (postId) => {
    const response = await fetch(`${API_BASE_URL}/posts/approve_post`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ post_id: postId }),
    });
    if (!response.ok) {
        throw new Error(`Error approving post: ${response.statusText}`);
    }
    return await response.json();
};

export const getLatestPrompt = async () => {
    const response = await fetch(`${API_BASE_URL}/prompts/latest`);
    if (!response.ok) {
        throw new Error(`Error fetching latest prompt: ${response.statusText}`);
    }
    return await response.json();
};

export const getPrompts = async () => {
    const response = await fetch(`${API_BASE_URL}/prompts`);
    if (!response.ok) {
        throw new Error(`Error fetching prompts: ${response.statusText}`);
    }
    return await response.json();
};

export const createPrompt = async (prompt) => {
    const response = await fetch(`${API_BASE_URL}/prompts`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
    });
    if (!response.ok) {
        throw new Error(`Error creating prompt: ${response.statusText}`);
    }
    return await response.json();
};

export const updatePrompt = async (promptId, content) => {
    const response = await fetch(`${API_BASE_URL}/prompts/${promptId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
    });
    if (!response.ok) {
        throw new Error(`Error updating prompt: ${response.statusText}`);
    }
    return await response.json();
};

export const updatePost = async (postId, content) => {
    console.log(postId, content)
    const response = await fetch(`${API_BASE_URL}/posts/${postId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
    });
    if (!response.ok) {
        throw new Error(`Error updating prompt: ${response.statusText}`);
    }
    return await response.json();
};

export const deletePrompt = async (promptId) => {
    const response = await fetch(`${API_BASE_URL}/prompts/${promptId}`, {
        method: 'DELETE',
    });
    if (!response.ok) {
        throw new Error(`Error deleting prompt: ${response.statusText}`);
    }
    return await response.json();
};
