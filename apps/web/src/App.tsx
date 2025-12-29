import { Route, Routes, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";
import { AppShell } from "./layouts/AppShell";
import { useAuth } from "./lib/auth";
import { apiGet } from "./lib/api";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Discover from "./pages/Discover";
import RoundDetail from "./pages/RoundDetail";
import Portfolio from "./pages/Portfolio";
import FounderDashboard from "./pages/FounderDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import Providers from "./pages/Providers";
import Disclaimer from "./pages/Disclaimer";

const PageWrapper = ({ children }: { children: React.ReactNode }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -10 }}
    transition={{ duration: 0.3 }}
  >
    {children}
  </motion.div>
);

export default function App() {
  const location = useLocation();
  const auth = useAuth();
  const [companyName, setCompanyName] = useState(
    auth.companyName ?? import.meta.env.VITE_COMPANY_NAME ?? "Radion"
  );

  useEffect(() => {
    apiGet<{ company: string }>("/health")
      .then((data) => setCompanyName(data.company))
      .catch(() => undefined);
  }, []);

  return (
    <AppShell role={auth.role} companyName={companyName}>
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<PageWrapper><Landing /></PageWrapper>} />
          <Route path="/login" element={<PageWrapper><Login /></PageWrapper>} />
          <Route path="/discover" element={<PageWrapper><Discover /></PageWrapper>} />
          <Route path="/rounds/:roundCode" element={<PageWrapper><RoundDetail /></PageWrapper>} />
          <Route path="/portfolio" element={<PageWrapper><Portfolio /></PageWrapper>} />
          <Route path="/founder" element={<PageWrapper><FounderDashboard /></PageWrapper>} />
          <Route path="/admin" element={<PageWrapper><AdminDashboard /></PageWrapper>} />
          <Route path="/providers" element={<PageWrapper><Providers /></PageWrapper>} />
          <Route path="/disclaimer" element={<PageWrapper><Disclaimer /></PageWrapper>} />
        </Routes>
      </AnimatePresence>
    </AppShell>
  );
}
