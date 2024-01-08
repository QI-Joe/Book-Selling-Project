import './App.css'

import { useEffect, useState } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { AlertContainer } from './components/alerts/AlertContainer'
import Navbar from './components/navbar/Navbar'
import Home from './pages/Home'
import Login from './pages/Login'
import Contribute from './pages/Login'

function App() {
  const [isInfoModalOpen, setIsInfoModalOpen] = useState(false)

  return (
    <div className="flex h-full flex-col">
      <Navbar setIsInfoModalOpen={setIsInfoModalOpen} />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/home" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/contribute" element={<Contribute />} />
      </Routes>

      <AlertContainer />
    </div>
  )
}

export default App
