import api from '../api/axios';

const studentService = {
  getDashboard: async () => {
    try {
      const response = await api.get('/student/dashboard/');
      // Backend returns { success: true, data: {...} }
      return response.data.data || response.data;
    } catch (error) {
      console.error('Error fetching student dashboard:', error);
      throw error;
    }
  },

  getResults: async () => {
    try {
      const response = await api.get('/student/results/');
      // Backend returns { success: true, data: [] }
      return response.data;
    } catch (error) {
      console.error('Error fetching student results:', error);
      throw error;
    }
  },

  getAttendance: async () => {
    try {
      const response = await api.get('/student/attendance/');
      // Backend returns { success: true, data: { attendance_percentage, total_records, present_records, absent_records, records: [] } }
      return response.data;
    } catch (error) {
      console.error('Error fetching student attendance:', error);
      throw error;
    }
  },

  getCGPA: async (studentId) => {
    try {
      const response = await api.get(`/students/${studentId}/cgpa/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching student CGPA:', error);
      throw error;
    }
  },

  getSessionCGPA: async (studentId, sessionId) => {
    try {
      const response = await api.get(`/students/${studentId}/cgpa/session/${sessionId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching session CGPA:', error);
      throw error;
    }
  },
};

export default studentService;
