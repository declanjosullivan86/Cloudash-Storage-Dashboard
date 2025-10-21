const { useState, useEffect, useCallback } = React;

// --- Helper Components ---
const Spinner = () => (
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
);

const ProviderLogo = ({ provider }) => {
    const logos = {
        'Google Drive': (
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 22l-8-8 4-14 12 4-8 18z" fill="#4285F4"/>
                <path d="M12 22l8-8-4-14-12 4z" fill="#34A853"/>
                <path d="M4 14l8 8 8-8-8-8z" fill="#FBBC05"/>
                <path d="M12 2l8 8-8 8-8-8z" fill="#EA4335"/>
            </svg>
        ),
        'Dropbox': (
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#0061FF" stroke="#0061FF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                 <path d="M4.2 8.4L9 5.2v3.2L4.2 11.6zm0 7.2l4.8-3.2v3.2L4.2 18.8zm5.6-5.6l4.8 3.2V10L9.8 6.8zm0 7.2l4.8 3.2V14l-4.8-3.2zM15 5.2l4.8 3.2L15 11.6V8.4zm0 11.2l4.8 3.2-4.8-3.2v-3.2z"/>
            </svg>
        ),
        'OneDrive': (
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#0078D4">
                <path d="M11.2,5.2a5.5,5.5,0,1,0,5.5,5.5A5.5,5.5,0,0,0,11.2,5.2ZM4,12.2a5,5,0,0,1,4.5-5H20a4,4,0,0,1,4,4V18a4,4,0,0,1-4,4H8a4,4,0,0,1-4-4Z"/>
            </svg>
        ),
    };
    return logos[provider] || null;
};

// --- Main Components ---
const Header = () => (
    <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8 flex items-center">
             <svg className="w-8 h-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 17H2a3 3 0 0 0 3-3V9a7 7 0 0 1 14 0v5a3 3 0 0 0 3 3zm-8.27 4a2 2 0 0 1-3.46 0"></path><path d="M12 22v-2"></path></svg>
            <h1 className="text-2xl font-bold text-gray-800 ml-2">CloudDash</h1>
        </div>
    </header>
);

const CloudAccountCard = ({ account, onDisconnect }) => {
    if (account.status === 'error') {
        return (
            <div className="bg-white rounded-xl shadow-lg p-6 flex flex-col justify-between transform hover:scale-105 transition-transform duration-300 border-2 border-red-200">
                <div className="flex items-center mb-4">
                    <ProviderLogo provider={account.provider} />
                    <h3 className="text-xl font-semibold text-gray-800 ml-3">{account.provider}</h3>
                </div>
                <div className="text-center text-red-500 font-medium my-4">
                    <p>Could not fetch data.</p>
                    <p>Please try reconnecting.</p>
                </div>
                 <button 
                    onClick={() => onDisconnect(account.id)}
                    className="w-full mt-4 bg-red-500 text-white font-bold py-2 px-4 rounded-lg hover:bg-red-600 transition-colors">
                    Disconnect
                </button>
            </div>
        );
    }
    
    const usagePercentage = account.storageTotal > 0 ? (account.storageUsed / account.storageTotal) * 100 : 0;
    const progressBarColor = usagePercentage > 85 ? 'bg-red-500' : usagePercentage > 60 ? 'bg-yellow-500' : 'bg-blue-500';

    return (
        <div className="bg-white rounded-xl shadow-lg p-6 flex flex-col justify-between transform hover:scale-105 transition-transform duration-300">
            <div>
                <div className="flex items-center mb-4">
                    <ProviderLogo provider={account.provider} />
                    <h3 className="text-xl font-semibold text-gray-800 ml-3">{account.provider}</h3>
                </div>
                <p className="text-sm text-gray-500 truncate mb-4">{account.email}</p>

                <div className="space-y-2">
                    <div className="flex justify-between items-center text-sm font-medium text-gray-600">
                        <span>Storage Usage</span>
                        <span>{usagePercentage.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div className={`${progressBarColor} h-2.5 rounded-full`} style={{ width: `${usagePercentage}%` }}></div>
                    </div>
                    <p className="text-right text-sm text-gray-500">{account.storageUsed} GB of {account.storageTotal} GB used</p>
                </div>

                {account.fileCount !== null && (
                     <div className="mt-4 pt-4 border-t border-gray-200">
                        <p className="text-sm font-medium text-gray-600">Total Items (Root): <span className="text-gray-800">{account.fileCount}</span></p>
                     </div>
                )}
            </div>
            
            <button 
                onClick={() => onDisconnect(account.id)}
                className="w-full mt-6 bg-gray-200 text-gray-700 font-bold py-2 px-4 rounded-lg hover:bg-red-500 hover:text-white transition-colors">
                Disconnect
            </button>
        </div>
    );
};

const AddAccountButton = ({ provider, id }) => {
    return (
        <a href={`/login/${id}`} className="bg-white rounded-xl shadow-lg p-6 flex flex-col items-center justify-center transform hover:scale-105 transition-transform duration-300 border-2 border-dashed border-gray-300 hover:border-blue-500 hover:text-blue-500 text-gray-600">
            <div className="flex items-center mb-3">
                <ProviderLogo provider={provider} />
                <h3 className="text-xl font-semibold ml-3">{provider}</h3>
            </div>
             <div className="flex items-center font-medium">
                <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
                Connect
            </div>
        </a>
    );
};

function App() {
    const [accounts, setAccounts] = useState([]);
    const [loading, setLoading] = useState(true);

    const availableProviders = [
        { id: 'google', provider: 'Google Drive'},
        { id: 'dropbox', provider: 'Dropbox'},
        { id: 'onedrive', provider: 'OneDrive'},
    ];

    const fetchAccounts = useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/accounts');
            const data = await response.json();
            setAccounts(data);
        } catch (error) {
            console.error("Failed to fetch accounts:", error);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchAccounts();
    }, [fetchAccounts]);
    
    const handleDisconnect = async (providerId) => {
        if (confirm(`Are you sure you want to disconnect ${providerId}?`)) {
            try {
                await fetch(`/api/disconnect/${providerId}`);
                // Refetch accounts to update UI
                fetchAccounts();
            } catch (error) {
                console.error("Failed to disconnect account:", error);
            }
        }
    };
    
    const connectedProviderIds = accounts.map(acc => acc.id);
    const unconnectedProviders = availableProviders.filter(p => !connectedProviderIds.includes(p.id));

    return (
        <div className="min-h-screen bg-gray-100">
            <Header />
            <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <div className="px-4 py-6 sm:px-0">
                    <h2 className="text-2xl font-semibold text-gray-700 mb-6">Your Cloud Accounts</h2>
                    
                    {loading ? (
                        <div className="flex justify-center items-center h-64">
                            <Spinner />
                        </div>
                    ) : (
                        <div>
                             {accounts.length === 0 && unconnectedProviders.length > 0 && (
                                <div className="text-center bg-white p-8 rounded-lg shadow-md">
                                    <h3 className="text-xl font-medium text-gray-700">Welcome to CloudDash!</h3>
                                    <p className="text-gray-500 mt-2">Connect your cloud storage accounts to see your stats here.</p>
                                </div>
                             )}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {accounts.map(acc => (
                                    <CloudAccountCard key={acc.id} account={acc} onDisconnect={handleDisconnect} />
                                ))}
                            </div>

                            {unconnectedProviders.length > 0 && (
                                <>
                                <h2 className="text-2xl font-semibold text-gray-700 mt-12 mb-6">Connect a New Account</h2>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {unconnectedProviders.map(p => <AddAccountButton key={p.id} {...p} />)}
                                </div>
                                </>
                            )}
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}

const container = document.getElementById('root');
const root = ReactDOM.createRoot(container);
root.render(<App />);
