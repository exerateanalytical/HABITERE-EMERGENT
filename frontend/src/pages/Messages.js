import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import { 
  Search, 
  Send, 
  MoreVertical, 
  Phone, 
  Video,
  Paperclip,
  Smile,
  ArrowLeft
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Messages = () => {
  const { user } = useAuth();
  const location = useLocation();
  
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (user) {
      fetchMessages();
    }
  }, [user]);

  useEffect(() => {
    // Handle pre-filled recipient from navigation state
    if (location.state?.recipientId && conversations.length > 0) {
      const conversation = conversations.find(c => 
        c.participants.some(p => p.id === location.state.recipientId)
      );
      if (conversation) {
        setSelectedConversation(conversation);
      }
    }
  }, [location.state, conversations]);

  const fetchMessages = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/messages`);
      
      // Group messages into conversations
      const messageGroups = {};
      
      response.data.forEach(message => {
        const otherUserId = message.sender_id === user.id ? message.receiver_id : message.sender_id;
        
        if (!messageGroups[otherUserId]) {
          messageGroups[otherUserId] = {
            id: otherUserId,
            participants: [
              { id: user.id, name: user.name, picture: user.picture },
              { 
                id: otherUserId, 
                name: `User ${otherUserId.slice(-4)}`, // Placeholder name
                picture: 'https://via.placeholder.com/40' 
              }
            ],
            messages: [],
            lastMessage: null,
            unreadCount: 0
          };
        }
        
        messageGroups[otherUserId].messages.push(message);
        
        // Update last message and unread count
        if (!messageGroups[otherUserId].lastMessage || 
            new Date(message.timestamp) > new Date(messageGroups[otherUserId].lastMessage.timestamp)) {
          messageGroups[otherUserId].lastMessage = message;
        }
        
        if (message.receiver_id === user.id && !message.is_read) {
          messageGroups[otherUserId].unreadCount++;
        }
      });

      // Sort conversations by last message time
      const conversationsList = Object.values(messageGroups).sort((a, b) => {
        if (!a.lastMessage) return 1;
        if (!b.lastMessage) return -1;
        return new Date(b.lastMessage.timestamp) - new Date(a.lastMessage.timestamp);
      });

      setConversations(conversationsList);
      
      // Set first conversation as selected if none selected
      if (conversationsList.length > 0 && !selectedConversation) {
        setSelectedConversation(conversationsList[0]);
      }
      
    } catch (error) {
      console.error('Error fetching messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectConversation = (conversation) => {
    setSelectedConversation(conversation);
    setMessages(conversation.messages.sort((a, b) => 
      new Date(a.timestamp) - new Date(b.timestamp)
    ));
    
    // Mark messages as read (this would be an API call in real app)
    conversation.unreadCount = 0;
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim() || !selectedConversation) return;
    
    try {
      setSendingMessage(true);
      
      const otherUser = selectedConversation.participants.find(p => p.id !== user.id);
      
      const messageData = {
        receiver_id: otherUser.id,
        content: newMessage.trim()
      };
      
      const response = await axios.post(`${API}/messages`, messageData);
      
      // Add message to current conversation
      const newMsg = response.data;
      setMessages(prev => [...prev, newMsg]);
      
      // Update conversation's last message
      setConversations(prev => prev.map(conv => 
        conv.id === selectedConversation.id 
          ? { ...conv, lastMessage: newMsg, messages: [...conv.messages, newMsg] }
          : conv
      ));
      
      setNewMessage('');
      
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setSendingMessage(false);
    }
  };

  const formatMessageTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } else {
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      });
    }
  };

  const filteredConversations = conversations.filter(conv => {
    const otherUser = conv.participants.find(p => p.id !== user?.id);
    return otherUser?.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
           conv.lastMessage?.content.toLowerCase().includes(searchQuery.toLowerCase());
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-xl shadow-sm h-[600px] flex">
            <div className="w-1/3 border-r border-gray-200 p-4">
              <div className="animate-pulse space-y-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gray-300 rounded-full"></div>
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-gray-300 rounded w-3/4"></div>
                      <div className="h-3 bg-gray-300 rounded w-1/2"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="flex-1 p-4">
              <div className="animate-pulse">
                <div className="h-6 bg-gray-300 rounded w-1/4 mb-6"></div>
                <div className="space-y-4">
                  <div className="h-4 bg-gray-300 rounded w-3/4 ml-auto"></div>
                  <div className="h-4 bg-gray-300 rounded w-1/2"></div>
                  <div className="h-4 bg-gray-300 rounded w-2/3 ml-auto"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" data-testid="messages-page">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl shadow-sm overflow-hidden h-[600px] flex">
          {/* Conversations List */}
          <div className="w-full md:w-1/3 border-r border-gray-200 flex flex-col">
            {/* Header */}
            <div className="p-4 border-b border-gray-200">
              <h1 className="text-xl font-semibold text-gray-900 mb-4">Messages</h1>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search conversations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  data-testid="search-conversations"
                />
              </div>
            </div>

            {/* Conversations */}
            <div className="flex-1 overflow-y-auto">
              {filteredConversations.length === 0 ? (
                <div className="p-8 text-center" data-testid="no-conversations">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Send className="w-8 h-8 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No conversations yet</h3>
                  <p className="text-gray-600">
                    Start a conversation by contacting property owners or service providers
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-gray-100">
                  {filteredConversations.map((conversation) => {
                    const otherUser = conversation.participants.find(p => p.id !== user?.id);
                    return (
                      <button
                        key={conversation.id}
                        onClick={() => selectConversation(conversation)}
                        className={`w-full p-4 hover:bg-gray-50 transition-colors text-left ${
                          selectedConversation?.id === conversation.id ? 'bg-blue-50' : ''
                        }`}
                        data-testid={`conversation-${conversation.id}`}
                      >
                        <div className="flex items-start space-x-3">
                          <div className="relative">
                            <img
                              src={otherUser?.picture || 'https://via.placeholder.com/40'}
                              alt={otherUser?.name}
                              className="w-12 h-12 rounded-full object-cover"
                            />
                            {conversation.unreadCount > 0 && (
                              <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                                {conversation.unreadCount}
                              </div>
                            )}
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            <div className="flex justify-between items-center mb-1">
                              <h3 className={`font-medium truncate ${
                                conversation.unreadCount > 0 ? 'text-gray-900' : 'text-gray-700'
                              }`}>
                                {otherUser?.name}
                              </h3>
                              {conversation.lastMessage && (
                                <span className="text-xs text-gray-500">
                                  {formatMessageTime(conversation.lastMessage.timestamp)}
                                </span>
                              )}
                            </div>
                            
                            {conversation.lastMessage && (
                              <p className={`text-sm truncate ${
                                conversation.unreadCount > 0 ? 'text-gray-900 font-medium' : 'text-gray-500'
                              }`}>
                                {conversation.lastMessage.sender_id === user?.id && 'You: '}
                                {conversation.lastMessage.content}
                              </p>
                            )}
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Chat Area */}
          <div className="flex-1 flex flex-col">
            {selectedConversation ? (
              <>
                {/* Chat Header */}
                <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <button className="md:hidden p-2 hover:bg-gray-100 rounded-lg">
                      <ArrowLeft className="w-5 h-5" />
                    </button>
                    
                    {(() => {
                      const otherUser = selectedConversation.participants.find(p => p.id !== user?.id);
                      return (
                        <div className="flex items-center space-x-3">
                          <img
                            src={otherUser?.picture || 'https://via.placeholder.com/40'}
                            alt={otherUser?.name}
                            className="w-10 h-10 rounded-full object-cover"
                          />
                          <div>
                            <h2 className="font-semibold text-gray-900">{otherUser?.name}</h2>
                            <p className="text-sm text-gray-500">Online</p>
                          </div>
                        </div>
                      );
                    })()}
                  </div>

                  <div className="flex items-center space-x-2">
                    <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                      <Phone className="w-5 h-5 text-gray-600" />
                    </button>
                    <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                      <Video className="w-5 h-5 text-gray-600" />
                    </button>
                    <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                      <MoreVertical className="w-5 h-5 text-gray-600" />
                    </button>
                  </div>
                </div>

                {/* Messages */}
                <div className="flex-1 p-4 overflow-y-auto space-y-4" data-testid="messages-container">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl shadow-sm ${
                          message.sender_id === user?.id
                            ? 'bg-blue-600 text-white'
                            : 'bg-white text-gray-900 border border-gray-200'
                        }`}
                      >
                        <p className="text-sm">{message.content}</p>
                        <p className={`text-xs mt-1 ${
                          message.sender_id === user?.id ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          {formatMessageTime(message.timestamp)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Message Input */}
                <div className="p-4 border-t border-gray-200">
                  <form onSubmit={sendMessage} className="flex items-center space-x-2">
                    <button
                      type="button"
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <Paperclip className="w-5 h-5 text-gray-600" />
                    </button>
                    
                    <div className="flex-1 relative">
                      <input
                        type="text"
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        placeholder="Type a message..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        disabled={sendingMessage}
                        data-testid="message-input"
                      />
                      <button
                        type="button"
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1 hover:bg-gray-100 rounded-full"
                      >
                        <Smile className="w-5 h-5 text-gray-600" />
                      </button>
                    </div>
                    
                    <button
                      type="submit"
                      disabled={!newMessage.trim() || sendingMessage}
                      className="p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-full transition-colors"
                      data-testid="send-message-btn"
                    >
                      <Send className="w-5 h-5" />
                    </button>
                  </form>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center" data-testid="no-conversation-selected">
                <div className="text-center">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Send className="w-8 h-8 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Select a conversation</h3>
                  <p className="text-gray-600">Choose a conversation from the list to start messaging</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Messages;