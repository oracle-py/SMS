import api from '../api/axios';

const studentService = {
  getDashboard: async () => {
    try {
      const response = await api.get('/student/dashboard/');
      // Backend returns data directly, not wrapped in a 'data' property
      return response.data;
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
};

export default studentService;
