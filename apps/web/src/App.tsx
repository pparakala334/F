import { Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";
import { AppShell } from "./layouts/AppShell";
import { AppLayout } from "./layouts/AppLayout";
import { useAuth } from "./lib/auth";
import { apiGet } from "./lib/api";
import Landing from "./pages/Landing";
import FounderDashboard from "./pages/FounderDashboard";
import InvestorDashboard from "./pages/InvestorDashboard";
import InvestorPortfolio from "./pages/InvestorPortfolio";
import InvestorPayouts from "./pages/InvestorPayouts";
import InvestorExits from "./pages/InvestorExits";
import FounderExits from "./pages/FounderExits";
import AdminDashboard from "./pages/AdminDashboard";
import AdminLedger from "./pages/AdminLedger";
import AuthPage from "./pages/AuthPage";

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
  const navigate = useNavigate();
  const auth = useAuth();
  const [companyName, setCompanyName] = useState(
    auth.companyName ?? import.meta.env.VITE_COMPANY_NAME ?? "Steelman"
  );

  useEffect(() => {
    apiGet<{ company: string }>("/health")
      .then((data) => setCompanyName(data.company))
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    auth.loadMe();
  }, [auth]);

  const handleAuthed = (role: string) => {
    if (role === "admin") {
      navigate("/app/admin");
    } else if (role === "investor") {
      navigate("/app/investor");
    } else {
      navigate("/app/founder");
    }
  };

  const isAppRoute = location.pathname.startsWith("/app");

  return (
    <>
      {!isAppRoute ? (
        <AppShell companyName={companyName} onSignIn={() => navigate("/auth")} showPublicNav>
          <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
              <Route path="/" element={<PageWrapper><Landing /></PageWrapper>} />
              <Route path="/auth" element={<PageWrapper><AuthPage onAuthed={handleAuthed} /></PageWrapper>} />
            </Routes>
          </AnimatePresence>
        </AppShell>
      ) : (
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            <Route
              path="/app/founder"
              element={
                <AppLayout role="founder" companyName={companyName}>
                  <FounderDashboard />
                </AppLayout>
              }
            />
            <Route
              path="/app/founder/exits"
              element={
                <AppLayout role="founder" companyName={companyName}>
                  <FounderExits />
                </AppLayout>
              }
            />
            <Route
              path="/app/investor"
              element={
                <AppLayout role="investor" companyName={companyName}>
                  <InvestorDashboard />
                </AppLayout>
              }
            />
            <Route
              path="/app/investor/portfolio"
              element={
                <AppLayout role="investor" companyName={companyName}>
                  <InvestorPortfolio />
                </AppLayout>
              }
            />
            <Route
              path="/app/investor/exits"
              element={
                <AppLayout role="investor" companyName={companyName}>
                  <InvestorExits />
                </AppLayout>
              }
            />
            <Route
              path="/app/investor/payouts"
              element={
                <AppLayout role="investor" companyName={companyName}>
                  <InvestorPayouts />
                </AppLayout>
              }
            />
            <Route
              path="/app/admin"
              element={
                <AppLayout role="admin" companyName={companyName}>
                  <AdminDashboard />
                </AppLayout>
              }
            />
            <Route
              path="/app/admin/ledger"
              element={
                <AppLayout role="admin" companyName={companyName}>
                  <AdminLedger />
                </AppLayout>
              }
            />
          </Routes>
        </AnimatePresence>
      )}
    </>
  );
}
