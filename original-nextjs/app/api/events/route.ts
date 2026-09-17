import { NextResponse } from "next/server"; import { prisma } from "@/lib/prisma";
export async function POST(req:Request){const {name,path,metadata}=await req.json();if(typeof name!=="string"||typeof path!=="string")return NextResponse.json({error:"Invalid event"},{status:400});await prisma.analyticsEvent.create({data:{name,path,metadata}});return NextResponse.json({ok:true})}
