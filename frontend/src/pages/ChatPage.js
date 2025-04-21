import React, { useState, useEffect } from "react";
import { Box, Typography, CircularProgress } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import "../styles/ChatPage.css";
import { useLocation, useNavigate } from "react-router-dom";
import { createAnswer, getChatHistory } from '../api/chatApi';

const ChatPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { deviceName, productId } = location.state || {};

  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  useEffect(() => {
    if (!deviceName || !productId) {
      navigate("/");
      return;
    }

    const loadPreviousChats = async () => {
      try {
        const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
        const userId = localStorage.getItem('userId');
        
        // 로그인한 경우에만 이전 대화 기록을 로드
        if (isLoggedIn && userId) {
          console.log("이전 대화 기록 불러오기 시작 - 제품 ID:", productId, "User ID:", userId);
          const response = await getChatHistory(productId, userId);
          console.log("받아온 대화 기록:", response);
          
          if (response && response.data && response.data.length > 0) {
            console.log("대화 기록을 메시지 형식으로 변환");
            const sortedData = [...response.data].sort((a, b) => 
              new Date(a.formattedQueryTime) - new Date(b.formattedQueryTime)
            );
            
            const newMessages = sortedData.flatMap(item => [
              {
                type: 'user',
                content: item.queryText,
                timestamp: item.formattedQueryTime
              },
              {
                type: 'assistant',
                content: item.responseText,
                timestamp: item.formattedQueryTime
              }
            ]);
            
            console.log("변환된 메시지:", newMessages);
            setMessages(newMessages);
          } else {
            // 대화 기록이 없는 경우 초기 인사말 표시
            setMessages([{
              type: 'assistant',
              content: "안녕하세요. 어떤 사용법을 알려드릴까요?",
              timestamp: new Date().toLocaleString('ko-KR')
            }]);
          }
        } else {
          // 로그인하지 않은 경우 초기 인사말만 표시
          setMessages([{
            type: 'assistant',
            content: "안녕하세요. 어떤 사용법을 알려드릴까요?",
            timestamp: new Date().toLocaleString('ko-KR')
          }]);
        }
      } catch (error) {
        console.error("대화 기록 불러오기 실패:", error);
        setMessages([{
          type: 'assistant',
          content: "안녕하세요. 어떤 사용법을 알려드릴까요?",
          timestamp: new Date().toLocaleString('ko-KR')
        }]);
      }
    };

    loadPreviousChats();
  }, [deviceName, productId, navigate]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const currentTime = new Date().toLocaleString('ko-KR');
    setMessages(prev => [...prev, { type: 'user', content: input, timestamp: currentTime }]);
    
    setMessages(prev => [...prev, { type: 'assistant', isLoading: true, timestamp: currentTime }]);
    setIsLoading(true);
    
    try {
      const collectionName = productId ? `product_${productId}_embeddings` : "langchain";
      const response = await createAnswer(
        input,
        collectionName,
        3
      );

      setMessages(prev => [
        ...prev.slice(0, -1),
        { type: 'assistant', content: response.answer, timestamp: new Date().toLocaleString('ko-KR') }
      ]);
    } catch (error) {
      console.error("답변 생성 실패:", error);
      setMessages(prev => [
        ...prev.slice(0, -1),
        { type: 'assistant', content: "죄송합니다. 답변을 생성하는 중에 문제가 발생했습니다. 다시 시도해주세요.", timestamp: new Date().toLocaleString('ko-KR') }
      ]);
    } finally {
      setIsLoading(false);
    }

    setInput("");
  };

  return (
    <Box className="chat-main">
      <Box className="chat-header">{deviceName}</Box>

      <Box className="chat-messages">
        {messages.map((msg, idx) => (
          <Box key={idx} className={`message ${msg.type}`}>
            {msg.isLoading ? (
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 1,
                padding: '8px'
              }}>
                <CircularProgress 
                  size={20} 
                  sx={{ 
                    color: '#666',
                    marginRight: '8px'
                  }} 
                />
                <Typography>답변 생성 중...</Typography>
              </Box>
            ) : (
              <>
                <Typography
                  sx={{
                    fontSize: '0.75rem',
                    color: '#666',
                    marginBottom: '4px'
                  }}
                >
                  {msg.timestamp}
                </Typography>
                {msg.content.split("\n").map((line, i) => (
                  <Typography
                    key={i}
                    component={i === 0 ? "div" : "p"}
                    sx={{
                      margin: i === 0 ? 0 : "4px 0",
                      whiteSpace: "pre-wrap",
                    }}
                  >
                    {line}
                  </Typography>
                ))}
              </>
            )}
          </Box>
        ))}
      </Box>

      <Box className="chat-input">
        <div className="input-container">
          <input
            type="text"
            placeholder="해당 제품의 궁금한 점을 질문하세요!"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !isLoading && handleSend()}
            disabled={isLoading}
          />
          <button 
            className="input-send-button" 
            onClick={handleSend}
            disabled={isLoading}
          >
            <SendIcon fontSize="small" />
          </button>
        </div>
      </Box>
    </Box>
  );
};

export default ChatPage;
