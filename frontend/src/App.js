import React, { useState, useEffect } from 'react';
import { 
  Button, TextField, List, ListItem, ListItemText, Box, 
  Container, Typography, Divider 
} from '@mui/material';

function App() {
  const [posts, setPosts] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [prompts, setPrompts] = useState([]);
  const [latestPrompt, setLatestPrompt] = useState('');
  const [editingPrompt, setEditingPrompt] = useState(null);
  const [groupedPosts, setGroupedPosts] = useState({});

  useEffect(() => {
    fetchGroupedPosts();
    getPrompts();
    getLatestPrompt();
  }, []);

  const fetchGroupedPosts = async () => {
    try {
      const response = await fetch('/get_grouped_posts');
      const data = await response.json();
      if (response.ok) {
        setGroupedPosts(data);
      } else {
        console.error('Failed to fetch grouped posts:', data.message);
      }
    } catch (error) {
      console.error("Error fetching grouped posts:", error);
    }
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
        fetchGroupedPosts();
        getLatestPrompt();
        setPrompt('');
      } else {
        alert(data.message || 'An error occurred while generating posts');
      }
    } catch (error) {
      console.error("There was a problem with the fetch operation: ", error);
      alert('An error occurred while generating posts');
    }
  };

  const approvePost = async (day, platform, content) => {
    try {
      await fetch('/api/approve_post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ day, platform, content })
      });
      fetchGroupedPosts();
    } catch (error) {
      console.error("Error approving post:", error);
      alert('An error occurred while approving the post');
    }
  };

  const getLatestPrompt = async () => {
    try {
      const response = await fetch('/get_latest_prompt');
      const data = await response.json();
      if (data.status === 'success' && data.data) {
        const parsedData = JSON.parse(data.data);
        setLatestPrompt(parsedData.content || '');
      } else {
        setLatestPrompt('');
      }
    } catch (error) {
      console.error("Error fetching latest prompt:", error);
      setLatestPrompt('');
    }
  };

  const getPrompts = async () => {
    try {
      const response = await fetch('/get_prompts');
      const data = await response.json();
      setPrompts(data);
    } catch (error) {
      console.error("Error fetching prompts:", error);
    }
  };

  const removePrompt = async (promptId) => {
    try {
      await fetch('/remove_prompt', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt_id: promptId })
      });
      getPrompts();
    } catch (error) {
      console.error("Error removing prompt:", error);
      alert('An error occurred while removing the prompt');
    }
  };

  const updatePrompt = async (promptId, content) => {
    try {
      const response = await fetch('/update_prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt_id: promptId.$oid || promptId, content })
      });
      if (response.ok) {
        setPrompts(prompts.map(p => p._id.$oid === promptId.$oid ? { ...p, content } : p));
        setEditingPrompt(null);
      } else {
        alert('Failed to update prompt');
      }
    } catch (error) {
      console.error("Error updating prompt:", error);
      alert('An error occurred while updating the prompt');
    }
  };

  return (
    <Container maxWidth="md">
      <Box my={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Previous Prompts
        </Typography>
        <List>
          {prompts.map((prompt) => (
            <ListItem key={prompt._id.$oid}>
              {editingPrompt === prompt._id.$oid ? (
                <>
                  <TextField
                    fullWidth
                    value={prompt.content}
                    onChange={(e) => setPrompts(prompts.map(p => 
                      p._id.$oid === prompt._id.$oid ? { ...p, content: e.target.value } : p
                    ))}
                    className="emoji-text"
                  />
                  <Button onClick={() => updatePrompt(prompt._id, prompt.content)}>Save</Button>
                  <Button onClick={() => setEditingPrompt(null)}>Cancel</Button>
                </>
              ) : (
                <>
                  <ListItemText 
                    primary={prompt.content} 
                    className="emoji-text"
                  />
                  <Button onClick={() => setEditingPrompt(prompt._id.$oid)}>Edit</Button>
                  <Button onClick={() => removePrompt(prompt._id)}>Remove</Button>
                </>
              )}
            </ListItem>
          ))}
        </List>
      </Box>
      <Box my={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Post Generator
        </Typography>
        <TextField
          fullWidth
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={latestPrompt || "Enter prompt for post generation"}
          margin="normal"
          className="emoji-text"
        />
        <Button variant="contained" color="primary" onClick={generatePosts}>
          Generate Posts
        </Button>
        
        {latestPrompt && (
          <Box mt={2}>
            <Typography variant="subtitle1" gutterBottom>
              Latest Prompt:
            </Typography>
            <Typography variant="body1" className="emoji-text">
              {latestPrompt}
            </Typography>
          </Box>
        )}

        <Box mt={4}>
          <Typography variant="h5" component="h2" gutterBottom>
            Generated Posts
          </Typography>
          {Object.entries(groupedPosts).map(([day, platforms]) => (
            <Box key={day} mb={3}>
              <Typography variant="h6" component="h3" gutterBottom>
                {day}
              </Typography>
              {Object.entries(platforms).map(([platform, contents]) => (
                <Box key={platform} mb={2}>
                  <Typography variant="subtitle1" gutterBottom>
                    {platform}
                  </Typography>
                  {contents.map((content, index) => (
                    <Box key={index} mb={1}>
                      <TextField
                        fullWidth
                        multiline
                        value={content}
                        onChange={(e) => {
                          const newGroupedPosts = JSON.parse(JSON.stringify(groupedPosts));
                          newGroupedPosts[day][platform][index] = e.target.value;
                          setGroupedPosts(newGroupedPosts);
                        }}
                        className="emoji-text"
                      />
                      <Button onClick={() => approvePost(day, platform, content)}>Approve</Button>
                    </Box>
                  ))}
                </Box>
              ))}
              <Divider />
            </Box>
          ))}
        </Box>
      </Box>
    </Container>
  );
}

export default App;