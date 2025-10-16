import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { 
  Search, 
  Send, 
  MessageSquare,
  ArrowLeft,
  User,
  Clock
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const Messages = () => {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  
  const [conversations, setConversations] = useState([]);
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [otherUser, setOtherUser] = useState(null);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchConversations();
    
    const userIdParam = searchParams.get('userId');
    if (userIdParam) {
      setSelectedUserId(userIdParam);
    }
  }, []);

  useEffect(() => {
    if (selectedUserId) {
      fetchMessageThread(selectedUserId);
      const interval = setInterval(() => {
        fetchMessageThread(selectedUserId);
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [selectedUserId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchConversations = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/api/messages/conversations`, {
        withCredentials: true
      });
      setConversations(response.data.conversations);
    } catch (err) {
      console.error('Error fetching conversations:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessageThread = async (userId) => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/messages/thread/${userId}`, {
        withCredentials: true
      });
      setMessages(response.data.messages);
      setOtherUser(response.data.other_user);
    } catch (err) {
      console.error('Error fetching messages:', err);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim() || !selectedUserId) return;

    try {
      setSendingMessage(true);
      await axios.post(
        `${BACKEND_URL}/api/messages`,
        {
          receiver_id: selectedUserId,
          content: newMessage.trim()
        },
        { withCredentials: true }
      );
      
      setNewMessage('');
      fetchMessageThread(selectedUserId);
      fetchConversations();
    } catch (err) {
      console.error('Error sending message:', err);
      alert(err.response?.data?.detail || 'Failed to send message');
    } finally {
      setSendingMessage(false);
    }
  };

  const filteredConversations = conversations.filter(conv =>
    conv.user_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    return date.toLocaleDateString();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <div className="flex h-[calc(100vh-64px)]">
          <div className={`${selectedUserId ? 'hidden md:block' : 'block'} w-full md:w-80 bg-white border-r border-gray-200`}>
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-xl font-bold mb-4 flex items-center">
                <MessageSquare className="w-6 h-6 mr-2" />
                Messages
              </h2>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search conversations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="overflow-y-auto" style={{ height: 'calc(100% - 140px)' }}>
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              ) : filteredConversations.length === 0 ? (
                <div className="text-center py-12 px-4">
                  <MessageSquare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No conversations yet</p>
                </div>
              ) : (
                filteredConversations.map((conv) => (
                  <button
                    key={conv.user_id}
                    onClick={() => setSelectedUserId(conv.user_id)}
                    className={`w-full p-4 flex items-start space-x-3 hover:bg-gray-50 transition-colors border-b ${
                      selectedUserId === conv.user_id ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className="flex-shrink-0">
                      {conv.user_picture ? (
                        <img
                          src={conv.user_picture}
                          alt={conv.user_name}
                          className="w-12 h-12 rounded-full object-cover"
                        />
                      ) : (
                        <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                          <User className="w-6 h-6 text-blue-600" />
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0 text-left">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-semibold text-gray-900 truncate">{conv.user_name}</h3>
                        {conv.unread_count > 0 && (
                          <span className="bg-blue-600 text-white text-xs font-bold px-2 py-1 rounded-full">
                            {conv.unread_count}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-500 truncate">
                        {conv.is_last_sender ? 'You: ' : ''}{conv.last_message}
                      </p>
                      <p className="text-xs text-gray-400 mt-1 flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        {formatTime(conv.last_message_time)}
                      </p>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>

          <div className={`${selectedUserId ? 'block' : 'hidden md:block'} flex-1 flex flex-col bg-white`}>
            {selectedUserId && otherUser ? (
              <>
                <div className="p-4 border-b border-gray-200 flex items-center">
                  <button onClick={() => setSelectedUserId(null)} className="md:hidden mr-3">
                    <ArrowLeft className="w-6 h-6" />
                  </button>
                  <div className="flex-shrink-0">
                    {otherUser.picture ? (
                      <img src={otherUser.picture} alt={otherUser.name} className="w-10 h-10 rounded-full" />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                        <User className="w-5 h-5 text-blue-600" />
                      </div>
                    )}
                  </div>
                  <div className="ml-3">
                    <h3 className="font-semibold">{otherUser.name}</h3>
                    <p className="text-sm text-gray-500 capitalize">{otherUser.role?.replace('_', ' ')}</p>
                  </div>
                </div>

                <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ maxHeight: 'calc(100vh - 240px)' }}>
                  {messages.map((message) => {
                    const isOwn = message.sender_id === user?.id;
                    return (
                      <div key={message.id} className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-xs md:max-w-md px-4 py-2 rounded-lg ${
                          isOwn ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'
                        }`}>
                          <p className="break-words">{message.content}</p>
                          <p className={`text-xs mt-1 ${isOwn ? 'text-blue-100' : 'text-gray-500'}`}>
                            {formatTime(message.timestamp)}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                  <div ref={messagesEndRef} />
                </div>

                <form onSubmit={handleSendMessage} className="p-4 border-t">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      placeholder="Type a message..."
                      className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      type="submit"
                      disabled={sendingMessage || !newMessage.trim()}
                      className="btn-primary px-6 disabled:opacity-50"
                    >
                      <Send className="w-5 h-5" />
                    </button>
                  </div>
                </form>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                  <MessageSquare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Select a conversation to start messaging</p>
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
