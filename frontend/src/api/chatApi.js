import axiosInstance from './axiosInstance';

export const savePdf = async (name, categoryId, file, onProgress) => {
    try {
        const formData = new FormData();
        formData.append('name', name);
        formData.append('categoryId', categoryId);
        formData.append('file', file);

        const response = await axiosInstance.post('/pdf/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
                const percentCompleted = Math.round(
                    (progressEvent.loaded * 100) / progressEvent.total
                );
                onProgress(percentCompleted);
            }
        });
        return response.data;
    } catch (error) {
        console.error("PDF 저장 실패:", error);
        throw error;
    }
};

export const createAnswer = async (query, collection_name, top_k) => {
    try {
        const body = {
            "query": query,
            "collection_name": collection_name,
            "top_k": top_k
          }

        const response = await axiosInstance.post('/chat/ask', body);
        return response.data;
    } catch (error) {
        console.error("답변 생성 실패:", error);
        throw error;
    }
};

export const getChatHistory = async (productId) => {
    try {
        console.log("대화 기록 조회 요청 시작 - 제품 ID:", productId);
        const response = await axiosInstance.get(`/chat/history?productId=${productId}`);
        console.log("대화 기록 조회 응답:", response);
        return response;
    } catch (error) {
        console.error("대화 기록 조회 실패:", error);
        throw error;
    }
};