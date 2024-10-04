import React, { useState, useEffect } from 'react';
import { Button, TextField, List, ListItem, ListItemText, Box, Container, Typography } from '@mui/material';

function App() {
  const [posts, setPosts] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [editingPost, setEditingPost] = useState(null);

  useEffect(() => {
    fetchPendingPosts();
  }, []);

  const fetchPendingPosts = async () => {
    const response = await fetch('/api/get_pending_posts');
    const data = await response.json();
    setPosts(data);
  };

  const generatePosts = async () => {
    try {
      const response = await fetch('/api/generate_posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      const data = await response.json();
      if (response.ok) {
        fetchPendingPosts();
      } else {
        alert(data.message || 'An error occurred while generating posts');
      }
    } catch (error) {
      console.error("There was a problem with the fetch operation: ", error);
      alert('An error occurred while generating posts');
    }
  };

  const approvePost = async (postId) => {
    await fetch('/api/approve_post', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ post_id: postId })
    });
    fetchPendingPosts();
  };

  const updatePost = async (postId, content) => {
    await fetch('/api/update_post', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ post_id: postId, content })
    });
    setEditingPost(null);
    fetchPendingPosts();
  };

  return (
    <Container maxWidth="md">
      <Box my={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Post Generator Admin
        </Typography>
        <TextField
          fullWidth
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter prompt for post generation"
          margin="normal"
        />
        <Button variant="contained" color="primary" onClick={generatePosts}>
          Generate Posts
        </Button>
        <List>
          {posts.map((post) => (
            <ListItem key={post._id}>
              {editingPost === post._id ? (
                <>
                  <TextField
                    fullWidth
                    value={post.content}
                    onChange={(e) => setPosts(posts.map(p => p._id === post._id ? {...p, content: e.target.value} : p))}
                  />
                  <Button onClick={() => updatePost(post._id, post.content)}>Save</Button>
                </>
              ) : (
                <>
                  <ListItemText primary={post.content} />
                  <Button onClick={() => setEditingPost(post._id)}>Edit</Button>
                  <Button onClick={() => approvePost(post._id)}>Approve</Button>
                </>
              )}
            </ListItem>
          ))}
        </List>
      </Box>
    </Container>
  );
}

export default App;