import type { Metadata } from "next";
import "./styles.css";
const site=process.env.NEXT_PUBLIC_SITE_URL||"http://localhost:3000";
export const metadata: Metadata={metadataBase:new URL(site),title:{default:"Falguni Chauhan | Portfolio",template:"%s | Falguni Chauhan"},description:"Portfolio of Falguni Chauhan, Social Media & Digital Marketing Strategist.",openGraph:{type:"website",siteName:"Falguni Chauhan"}};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
