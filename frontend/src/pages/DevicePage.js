import FavoriteIcon from "@mui/icons-material/Favorite";
import FavoriteBorderIcon from "@mui/icons-material/FavoriteBorder";
import { Box, Typography, TextField, FormControlLabel, Switch, Tooltip } from "@mui/material";
import React, { useEffect, useState, useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { productList } from "../api/productApi";
import { addFavorite, deleteFavorite, favoriteList } from "../api/favoriteApi";
import { setProducts } from "../redux/ProductSlice";
// import { loginSuccess } from "../redux/LoginSlice";
import { updateFavorites } from "../redux/LoginSlice";
import "../styles/DevicePage.css";
import InfoIcon from '@mui/icons-material/Info';

const DevicePage = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [searchQuery, setSearchQuery] = useState("");
  const [isAISearch, setIsAISearch] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const products = useSelector((state) => state.product.products) || [];
  const userFavorites = useSelector((state) => state.login.favoriteList) || [];
  const userId = useSelector((state) => state.login.user?.id);
  // const user = useSelector((state) => state.login.user);

  const fetchProducts = useCallback(async () => {
    try {
      const data = await productList();
      dispatch(setProducts(data));
    } catch (error) {
      console.error("제품 목록 가져오기 실패:", error);
    }
  }, [dispatch]);

  const fetchFavorites = useCallback(async () => {
    if (!userId) return;
    
    try {
      const favorites = await favoriteList(userId);
      if (Array.isArray(favorites)) {
        // Redux 상태 업데이트
        dispatch(updateFavorites(favorites));
        
        // localStorage 업데이트
        const storedUser = localStorage.getItem("user");
        if (storedUser) {
          const userData = JSON.parse(storedUser);
          localStorage.setItem("user", JSON.stringify({
            ...userData,
            favoriteList: favorites
          }));
        }
      }
    } catch (error) {
      console.error("즐겨찾기 목록 가져오기 실패:", error);
      
      // 에러 발생 시 localStorage의 데이터 사용
      const storedUser = localStorage.getItem("user");
      if (storedUser) {
        const userData = JSON.parse(storedUser);
        dispatch(updateFavorites(userData.favoriteList || []));
      }
    }
  }, [userId, dispatch]);

  // 초기 데이터 로드
  useEffect(() => {
    fetchProducts();
    fetchFavorites();
  }, [fetchProducts, fetchFavorites]);

  // 검색 처리 함수
  const handleSearch = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      if (isAISearch) {
        // AI 검색 로직은 추후 구현
        console.log("AI 검색 기능 준비 중입니다.");
        return;
      }

      // 기존 검색 로직
      const filtered = products.filter((device) => 
        device?.name?.toLowerCase().includes(query.toLowerCase())
      );
      setSearchResults(filtered);
    } catch (error) {
      console.error("검색 중 오류 발생:", error);
      setSearchResults([]);
    }
  };

  // 검색어 변경 핸들러
  const handleSearchChange = (e) => {
    const newQuery = e.target.value;
    setSearchQuery(newQuery);
    handleSearch(newQuery);  // 검색어 변경시마다 검색 실행
  };

  // AI 검색 모드 변경 핸들러
  const handleAISearchToggle = (e) => {
    setIsAISearch(e.target.checked);
    setSearchQuery("");  // 검색어 초기화
    setSearchResults([]); // 검색 결과 초기화
  };

  // 표시할 디바이스 목록 결정
  const displayedDevices = searchQuery.trim() ? searchResults : products;

  const handleDeviceClick = (device) => {
    navigate("/chat", { state: { deviceName: device.name, productId: device.id } });
  };

  const isFavorite = (productId) => {
    return userFavorites.includes(productId);
  };

  const toggleFavorite = async (e, deviceId) => {
    e.stopPropagation();

    if (!userId) {
      alert("로그인이 필요합니다.");
      return;
    }

    if (isProcessing) return;

    setIsProcessing(true);
    try {
      let newFavorites;
      if (isFavorite(deviceId)) {
        await deleteFavorite(userId, deviceId);
        newFavorites = userFavorites.filter(id => id !== deviceId);
      } else {
        await addFavorite(userId, deviceId);
        newFavorites = [...userFavorites, deviceId];
      }
      
      // Redux 상태 업데이트
      dispatch(updateFavorites(newFavorites));
      
      // localStorage 업데이트
      const storedUser = localStorage.getItem("user");
      if (storedUser) {
        const userData = JSON.parse(storedUser);
        localStorage.setItem("user", JSON.stringify({
          ...userData,
          favoriteList: newFavorites
        }));
      }
    } catch (error) {
      console.error("즐겨찾기 토글 실패:", error);
      alert("즐겨찾기 처리 중 오류가 발생했습니다.");
      await fetchFavorites(); // 실패 시 서버에서 최신 데이터 다시 가져오기
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ 
        display: 'flex', 
        gap: 2, 
        mb: 3, 
        alignItems: 'center',
        maxWidth: '800px',
        mx: 'auto'
      }}>
        <TextField
          fullWidth
          placeholder={isAISearch ? "제품 특징으로 원하는 모델을 검색하세요." : "제품 모델명으로 검색하세요."}
          value={searchQuery}
          onChange={handleSearchChange}
          sx={{
            '& .MuiOutlinedInput-root': {
              backgroundColor: 'white',
              borderRadius: 2
            }
          }}
        />
        
        <FormControlLabel
          control={
            <Switch
              checked={isAISearch}
              onChange={handleAISearchToggle}
              color="primary"
              size="small"
            />
          }
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Typography variant="body2" sx={{ fontSize: '0.875rem', whiteSpace: 'nowrap' }}>
                AI 검색
              </Typography>
              <Tooltip 
                title="AI를 활용하여 검색할 수 있습니다"
                placement="top"
              >
                <InfoIcon sx={{ fontSize: '1rem' }} color="action" />
              </Tooltip>
            </Box>
          }
          sx={{
            margin: 0,
            marginLeft: 1,
            '.MuiFormControlLabel-label': {
              marginLeft: 0.5
            }
          }}
        />
      </Box>

      <Box className="device-grid">
        {displayedDevices.map((device) => (
          <Box
            key={device.id}
            className="device-item"
            onClick={() => handleDeviceClick(device)}
          >
            <Box className="device-icon-container">
              <img
                src={device.icon}
                alt={device.name}
                style={{ width: "54px", height: "54px" }}
              />
              <div
                className={`favorite-icon ${isFavorite(device.id) ? "active" : ""}`}
                onClick={(e) => toggleFavorite(e, device.id)}
              >
                {isFavorite(device.id) ? (
                  <FavoriteIcon fontSize="small" />
                ) : (
                  <FavoriteBorderIcon fontSize="small" />
                )}
              </div>
            </Box>
            <Typography className="device-name">{device.name}</Typography>
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default DevicePage;