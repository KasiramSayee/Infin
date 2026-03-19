import React, { useState } from 'react';
import { Shield, ChevronRight, X, ExternalLink, ShieldCheck } from 'lucide-react';

const Dashboard = ({ user, onLogout, onGoToPolicy }) => {
  const [showTerms, setShowTerms] = useState(false);
  const [showFullTerms, setShowFullTerms] = useState(false);
  const [accepted, setAccepted] = useState(false);

  const handleAccept = () => {
    setShowTerms(false);
    onGoToPolicy();
  };

  return (
    <div className="min-h-screen bg-[#1F1F1F] p-4 md:p-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8 max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <ShieldCheck className="text-[#0066FF] w-8 h-8"/> InFin
        </h1>
        <button
          onClick={onLogout}
          className="text-gray-400 hover:text-white transition-colors"
        >
          Logout
        </button>
      </div>

      <div className="max-w-4xl mx-auto space-y-6">
        
        {/* Welcome Card */}
        <div className="bg-[#2B2B2B] rounded-2xl p-8 border border-white/5 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-[#0066FF]/10 rounded-full blur-[80px] pointer-events-none"></div>
          
          <h2 className="text-3xl font-bold text-white mb-2">Hello, {user?.platform || 'Worker'} Partner!</h2>
          <p className="text-gray-400 mb-8 max-w-md">
            Protect your daily earnings against unexpected weather and zone disruptions. No claims to file, just peace of mind.
          </p>

          <button
            onClick={() => setShowTerms(true)}
            className="bg-[#0066FF] hover:bg-[#0052cc] text-white font-semibold flex items-center gap-2 py-4 px-8 rounded-xl transition-all hover:scale-[1.02] shadow-lg shadow-blue-500/20 text-lg"
          >
            <Shield className="w-5 h-5" /> Get Insurance Now <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-[#2B2B2B] p-6 rounded-2xl border border-white/5 shadow-lg">
            <h3 className="text-sm text-gray-400 font-medium mb-1">Active Policy</h3>
            <p className="text-2xl font-bold text-white">None</p>
          </div>
          <div className="bg-[#2B2B2B] p-6 rounded-2xl border border-white/5 shadow-lg">
            <h3 className="text-sm text-gray-400 font-medium mb-1">Protected Income</h3>
            <p className="text-2xl font-bold text-white">₹0</p>
          </div>
          <div className="bg-[#2B2B2B] p-6 rounded-2xl border border-white/5 shadow-lg">
            <h3 className="text-sm text-gray-400 font-medium mb-1">Recent Claims</h3>
            <p className="text-2xl font-bold text-gray-500">No history</p>
          </div>
        </div>

      </div>

      {/* Terms Modal */}
      {showTerms && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-[#222] w-full max-w-lg rounded-2xl border border-[#444] shadow-2xl flex flex-col overflow-hidden max-h-[90vh]">
            
            {/* Modal Header */}
            <div className="flex justify-between items-center p-6 border-b border-[#333]">
              <h3 className="text-xl font-bold text-white">Coverage Terms & Conditions</h3>
              <button onClick={() => setShowTerms(false)} className="text-gray-400 hover:text-white">
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto">
              <p className="text-gray-300 mb-4 leading-relaxed text-sm">
                Before proceeding to calculate your personalized weekly premium, please review how InFin's parametric system works. Your policy strictly relies on automated data triggers from trusted meteorological and civic APIs.
              </p>

              {/* Expandable full terms inside same popup */}
              <div className="mb-6">
                <button 
                  onClick={() => setShowFullTerms(!showFullTerms)}
                  className="text-[#0066FF] font-medium text-sm flex items-center gap-1 hover:underline outline-none"
                >
                  <ExternalLink className="w-4 h-4" /> 
                  {showFullTerms ? 'Hide Full Legal Terms' : 'Read Full Terms & Conditions'}
                </button>
                
                {showFullTerms && (
                  <div className="mt-4 p-4 bg-[#1A1A1A] rounded-lg border border-[#333] text-xs text-gray-400 space-y-3 h-48 overflow-y-auto custom-scrollbar">
                    <p><strong>1. Policy Activation:</strong> Coverage begins immediately upon successful payment of your weekly premium. The 6-hour refractory period applies for spontaneous disruption events (e.g. riots, unplanned barricading).</p>
                    <p><strong>2. Payout Gates:</strong> Claim payouts are strictly evaluated using the 3-Gate Check (DVS, ZPCS, AEC). Traditional damage claims are not entertained. Valid disbursements happen automatically via UPI.</p>
                    <p><strong>3. Anti-Gaming Clause:</strong> Policies bought *after* an official public disruption alert (e.g. IMD Orange/Red alert, strike announcement) are excluded from coverage for that specific event.</p>
                    <p><strong>4. Dispute Resolution:</strong> All external API data snapshots used for gate validity are final. Manual audit requests are subject to internal operational capacities.</p>
                    <p><strong>5. Loyalty Bonus:</strong> A minimum of 24 concurrent weekly payments without any claims grants a partial return of premiums. A single missed week resets your standing.</p>
                  </div>
                )}
              </div>

              <label className="flex items-start gap-3 cursor-pointer group">
                <div className="mt-1">
                  <input 
                    type="checkbox" 
                    checked={accepted}
                    onChange={(e) => setAccepted(e.target.checked)}
                    className="w-5 h-5 rounded border-[#444] text-[#0066FF] focus:ring-[#0066FF] focus:ring-offset-[#222] bg-[#1A1A1A] cursor-pointer"
                  />
                </div>
                <span className="text-sm text-gray-400 group-hover:text-gray-300 transition-colors">
                  I have read and agree to the parametric insurance guidelines, automatic gate evaluation process, and the 6-hour spontaneous event refractory rule.
                </span>
              </label>
            </div>

            {/* Modal Footer */}
            <div className="p-6 border-t border-[#333] flex gap-3 justify-end bg-[#1A1A1A]">
              <button 
                onClick={() => setShowTerms(false)}
                className="px-6 py-2 rounded-lg font-medium text-gray-400 hover:text-white transition-colors border border-transparent hover:border-[#444]"
              >
                Cancel
              </button>
              <button 
                onClick={handleAccept}
                disabled={!accepted}
                className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                  accepted 
                  ? 'bg-[#0066FF] hover:bg-[#0052cc] text-white shadow-lg shadow-blue-500/20' 
                  : 'bg-[#333] text-gray-500 cursor-not-allowed'
                }`}
              >
                Accept & Continue
              </button>
            </div>

          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
