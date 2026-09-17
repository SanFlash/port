CREATE TYPE "Visibility" AS ENUM ('DRAFT', 'PUBLISHED', 'PRIVATE', 'ARCHIVED');
CREATE TABLE "Profile" ("id" TEXT PRIMARY KEY, "name" TEXT NOT NULL, "headline" TEXT NOT NULL, "location" TEXT, "email" TEXT, "phone" TEXT, "intro" TEXT, "summary" TEXT, "updatedAt" TIMESTAMP(3) NOT NULL);
CREATE TABLE "CollectionItem" ("id" TEXT PRIMARY KEY, "collection" TEXT NOT NULL, "title" TEXT NOT NULL, "slug" TEXT UNIQUE, "status" "Visibility" NOT NULL DEFAULT 'DRAFT', "featured" BOOLEAN NOT NULL DEFAULT false, "position" INTEGER NOT NULL DEFAULT 0, "data" JSONB NOT NULL, "source" TEXT NOT NULL DEFAULT 'manual', "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP, "updatedAt" TIMESTAMP(3) NOT NULL);
CREATE INDEX "CollectionItem_collection_status_position_idx" ON "CollectionItem"("collection", "status", "position");
CREATE TABLE "Media" ("id" TEXT PRIMARY KEY, "name" TEXT NOT NULL, "url" TEXT NOT NULL, "mimeType" TEXT NOT NULL, "size" INTEGER, "alt" TEXT, "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE "ContactSubmission" ("id" TEXT PRIMARY KEY, "name" TEXT NOT NULL, "email" TEXT NOT NULL, "company" TEXT, "message" TEXT NOT NULL, "projectType" TEXT, "budget" TEXT, "timeline" TEXT, "status" TEXT NOT NULL DEFAULT 'new', "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE "AnalyticsEvent" ("id" TEXT PRIMARY KEY, "name" TEXT NOT NULL, "path" TEXT NOT NULL, "metadata" JSONB, "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX "AnalyticsEvent_createdAt_path_idx" ON "AnalyticsEvent"("createdAt", "path");
