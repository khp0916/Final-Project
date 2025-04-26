import axiosInstance from './axiosInstance';

export const productList = async () => {
    try {
        const response = await axiosInstance.get('/product/list');
        return response.data;
    } catch (error) {
        console.error("제품 전체조회 실패:", error);
        throw error;
    }
};

export const aiSearch = async (query) => {
    try {
        const response = await axiosInstance.post('/product/ai-search', { query });
        return response.data;
    } catch (error) {
        console.error("AI 검색 실패:", error);
        throw error;
    }
};