import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Header } from './components/Header'
import DashboardPage from './pages/DashboardPage'
import { SourceListPage } from './pages/SourceListPage'
import { SourceFormPage } from './pages/SourceFormPage'
import { CompanyListPage } from './pages/CompanyListPage'
import { CompanyFormPage } from './pages/CompanyFormPage'
import { VacancyListPage } from './pages/VacancyListPage'
import { VacancyDetailPage } from './pages/VacancyDetailPage'
import { VacancyFormPage } from './pages/VacancyFormPage'

export default function App() {
  return (
    <BrowserRouter>
      <div className="background-blobs">
        <div className="blob blob-1" />
        <div className="blob blob-2" />
      </div>

      <Header />

      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/vacancies" element={<VacancyListPage />} />
        <Route path="/vacancies/new" element={<VacancyFormPage />} />
        <Route path="/vacancies/:id" element={<VacancyDetailPage />} />
        <Route path="/vacancies/:id/edit" element={<VacancyFormPage />} />
        <Route path="/sources" element={<SourceListPage />} />
        <Route path="/sources/new" element={<SourceFormPage />} />
        <Route path="/sources/:id/edit" element={<SourceFormPage />} />
        <Route path="/companies" element={<CompanyListPage />} />
        <Route path="/companies/new" element={<CompanyFormPage />} />
      </Routes>
    </BrowserRouter>
  )
}