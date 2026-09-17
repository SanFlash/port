import { isAdmin } from "@/lib/auth"; import AdminClient from "./client";
export default async function Admin(){return <AdminClient authenticated={await isAdmin()}/>}
