import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const searchRoutes = (from, to, date, maxHops = 2) =>
  api.get('/routes/search/', { params: { from, to, date, max_hops: maxHops } })

export const aiSearch = (query) =>
  api.post('/routes/ai-search/', { query })

export const stationSearch = (q) =>
  api.get('/stations/search/', { params: { q } })

export const getPopularRoutes = () =>
  api.get('/routes/popular/')

export const getTrainStatus = (trainNo, date) =>
  api.get('/train/status/', { params: { train_no: trainNo, date } })

export const getSeatAvailability = (trainNo, from, to, date, quota = 'GN', classCode = 'SL') =>
  api.get('/train/seat-availability/', {
    params: {
      train_no: trainNo,
      from,
      to,
      date,
      quota,
      class_code: classCode,
    },
  })
