import { SignJWT, jwtVerify } from "jose";
import { cookies } from "next/headers";
const key = () => new TextEncoder().encode(process.env.AUTH_SECRET || "development-only-change-me-before-production");
export async function signAdmin(){ return new SignJWT({role:"admin"}).setProtectedHeader({alg:"HS256"}).setIssuedAt().setExpirationTime("8h").sign(key()); }
export async function isAdmin(){ const token=(await cookies()).get("portfolio_admin")?.value; if(!token) return false; try { return (await jwtVerify(token,key())).payload.role === "admin"; } catch { return false; } }
