// App.js
import React, { useState, useEffect } from 'react';
import {
  Button, TextField, List, ListItem, ListItemText, Box,
  Container, Typography, Divider
} from '@mui/material';
import {
  getGroupedPosts,
  generatePosts,
  approvePost,
  getLatestPrompt,
  getPrompts,
  createPrompt,
  updatePrompt,
  deletePrompt,
  updatePost
} from './apiService';

function App() {
  const [groupedPosts, setGroupedPosts] = useState({});
  const [prompt, setPrompt] = useState('');
  const [prompts, setPrompts] = useState([]);
  const [latestPrompt, setLatestPrompt] = useState('');
  const [editingPromptId, setEditingPromptId] = useState(null);
  const [editingPromptContent, setEditingPromptContent] = useState('');
  const [editingPostId, setEditingPostId] = useState(null);
  const [editingPostContent, setEditingPostContent] = useState({});

  useEffect(() => {
    fetchGroupedPosts();
    fetchPrompts();
    fetchLatestPrompt();
  }, []);

  // Function to clean posts
  const cleanPosts = (groupedPosts) => {
    Object.entries(groupedPosts).forEach(([day, platforms]) => {
      Object.entries(platforms).forEach(([platform, posts]) => {
        console.log(`Cleaning posts for ${day} - ${platform}:`, posts); // Log the posts before cleaning
        groupedPosts[day][platform] = posts.map(post => {
          // Strip out day and platform info using regex
          const cleanedPost = post.content.replace(/^[A-Za-zıİçÇğĞşŞ]+:\n\[Platform:\s*\w+\]\n?/g, '').trim();
          console.log('Original Post:', post); // Log each original post for comparison
          console.log('Cleaned Post:', cleanedPost); // Log each cleaned post

          // Return an object with the cleaned content and the original ID
          return {
            id: post.id,  // Keep the original ID
            content: cleanedPost // Use the cleaned content
          };
        });
      });
    });
  };



  const fetchGroupedPosts = async () => {
    try {
      const response = await fetch('/api/posts/grouped');

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      console.log('Original Data:', JSON.stringify(data, null, 2)); // Log the original response structure

      // Clean the posts after fetching the data
      cleanPosts(data);
      console.log('Cleaned Data:', JSON.stringify(data, null, 2)); // Log the cleaned posts

      setGroupedPosts(data); // Update state with cleaned posts
    } catch (error) {
      console.error('Fetch error:', error);
    }
  };

  const handleGeneratePosts = async () => {
    if (!prompt) return;

    try {
      await generatePosts(prompt);
      setPrompt('');
      fetchGroupedPosts();
      fetchLatestPrompt();
      fetchPrompts();
    } catch (error) {
      console.error('Error generating posts:', error);
      alert('An error occurred while generating posts');
    }
  };

  const handleApprovePost = async (postId) => {
    try {
      await approvePost(postId);
      fetchGroupedPosts();
    } catch (error) {
      console.error('Error approving post:', error);
      alert('An error occurred while approving the post');
    }
  };

  const handleUpdatePost = async (postId) => {
    console.log('updating:' + postId + " " + editingPostContent)
    if (!editingPostContent) return;

    try {
      await updatePost(postId, { content: editingPostContent });
      setEditingPostId(null); // Reset editing state
      setEditingPostContent(''); // Clear the input
      fetchGroupedPosts();
    } catch (error) {
      console.error('Error updating post:', error);
      alert('An error occurred while updating the post');
    }
  };

  const fetchLatestPrompt = async () => {
    try {
      const response = await getLatestPrompt();
      if (response.status === 'success') {
        setLatestPrompt(response.prompt || '');
      } else {
        setLatestPrompt('');
      }
    } catch (error) {
      console.error('Error fetching latest prompt:', error);
      setLatestPrompt('');
    }
  };

  const fetchPrompts = async () => {
    try {
      const response = await getPrompts();
      setPrompts(response.data.prompts || []);
    } catch (error) {
      console.error('Error fetching prompts:', error);
    }
  };

  const handleCreatePrompt = async () => {
    if (!prompt) return;

    try {
      await createPrompt(prompt);
      setPrompt('');
      fetchPrompts();
    } catch (error) {
      console.error('Error creating prompt:', error);
      alert('An error occurred while creating the prompt');
    }
  };

  const handleUpdatePrompt = async () => {
    console.log('updating:' + editingPromptId + " " + editingPromptContent)
    if (!editingPromptId || !editingPromptContent) return;

    try {
      await updatePrompt(editingPromptId, editingPromptContent);
      setEditingPromptId(null);
      setEditingPromptContent('');
      fetchPrompts();
    } catch (error) {
      console.error('Error updating prompt:', error);
      alert('An error occurred while updating the prompt');
    }
  };

  const handleDeletePrompt = async (promptId) => {
    try {
      await deletePrompt(promptId);
      fetchPrompts();
    } catch (error) {
      console.error('Error deleting prompt:', error);
      alert('An error occurred while deleting the prompt');
    }
  };

  return (
    <Container maxWidth="md">
      <Box my={4}>
        <Typography variant="h4" gutterBottom>
          Post Generator
        </Typography>
        <TextField
          fullWidth
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={latestPrompt || 'Enter prompt for post generation'}
          margin="normal"
          multiline
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleGeneratePosts}
          disabled={!prompt.trim()}
        >
          Generate Posts
        </Button>

        {latestPrompt && (
          <Box mt={2}>
            <Typography variant="subtitle1" gutterBottom>
              Latest Prompt:
            </Typography>
            <Typography variant="body1">
              {latestPrompt}
            </Typography>
          </Box>
        )}
      </Box>

      {Object.entries(groupedPosts).map(([day, platforms]) => (
        <Box key={day} mb={3}>
          <Typography variant="h6" gutterBottom>
            {day}
          </Typography>
          {Object.entries(platforms).map(([platform, posts]) => (
            <Box key={platform} mb={2}>
              <Typography variant="subtitle1" gutterBottom>
                {platform}
              </Typography>
              {Array.isArray(posts) && posts.length > 0 ? (
                posts.map((post) => (
                  <Box key={post.id} mb={1}>
                    <TextField
                      fullWidth
                      multiline
                      value={editingPostId === post.id ? editingPostContent : post.content}
                      onChange={(e) => {
                        setEditingPostId(post.id);
                        setEditingPostContent(e.target.value); // Directly update the content
                      }}
                    />
                    <Button
                      variant="outlined"
                      color="primary"
                      onClick={() => {
                        // When clicking "Edit", set the current post's content for editing
                        setEditingPostId(post.id);
                        setEditingPostContent(post.content);
                        console.log(`Editing post ID: ${post.id}, Content: ${post.content}`);
                      }}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="outlined"
                      color="primary"
                      onClick={() => {
                        handleUpdatePost(post.id);
                        console.log(`Saving post ID: ${post.id} with Content: ${editingPostContent}`);
                      }}
                    >
                      Save
                    </Button>
                    <Button
                      variant="outlined"
                      color="primary"
                      onClick={() => handleApprovePost(post.id)}
                    >
                      Approve
                    </Button>
                  </Box>
                ))
              ) : (
                <Typography color="error">No posts available</Typography>
              )}
            </Box>
          ))}
          <Divider />
        </Box>
      ))}

      <Box my={4}>
        <Typography variant="h4" gutterBottom>
          Previous Prompts
        </Typography>
        <List>
          {prompts.map((prompt) => (
            <ListItem key={prompt._id}>
              {editingPromptId === prompt._id ? (
                <>
                  <TextField
                    fullWidth
                    multiline
                    value={editingPromptContent}
                    onChange={(e) => setEditingPromptContent(e.target.value)}
                  />
                  <Button onClick={handleUpdatePrompt}>Save</Button>
                  <Button onClick={() => setEditingPromptId(null)}>Cancel</Button>
                </>
              ) : (
                <>
                  <ListItemText
                    primary={prompt.content}
                  />
                  <Button onClick={() => {
                    setEditingPromptId(prompt._id);
                    setEditingPromptContent(prompt.content);
                  }}>
                    Edit
                  </Button>
                  <Button onClick={() => handleDeletePrompt(prompt._id)}>
                    Remove
                  </Button>
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