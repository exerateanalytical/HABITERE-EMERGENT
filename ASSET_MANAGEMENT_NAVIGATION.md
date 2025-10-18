# Asset Management Navigation Guide

## Where to Find Asset Management

### 1. **For Logged-In Users (Main Navigation)**
When you're logged in, the **"Assets"** link appears in the user dropdown menu with a Package icon (📦).

**Location:** 
- Desktop: Top-right navbar → Click on your profile/user icon → "Assets" option
- Mobile: Hamburger menu (☰) → "Assets" option

**Path:** `/assets/dashboard`

### 2. **Footer (All Users)**
The **"Asset Management"** link is now available in the footer under the "Resources" section.

**Location:**
- Scroll to bottom of any page
- Look for "Resources" section
- Click "Asset Management"

**Path:** `/assets/dashboard`

---

## Why Asset Management Requires Login

Asset Management is a **protected feature** designed for:
- Property Owners
- Estate Managers  
- Technicians
- Administrators

Since it involves managing sensitive property assets, maintenance schedules, and expenses, it requires authentication for security.

---

## How to Access Asset Management

### Step 1: Login
1. Click "Sign In" in the top-right corner
2. Enter your credentials
3. After successful login, you'll see your profile menu

### Step 2: Navigate to Assets
**Option A - From Navbar:**
1. Click on your profile icon/name in top-right
2. Click "Assets" (with Package icon)
3. You'll be taken to the Asset Dashboard

**Option B - From Footer:**
1. Scroll to the bottom of any page
2. Under "Resources", click "Asset Management"
3. If not logged in, you'll be redirected to login first

### Step 3: Use Asset Management Features
Once in the Asset Dashboard, you can:
- View asset statistics
- Manage assets inventory
- Schedule maintenance tasks
- Track expenses
- View upcoming maintenance alerts

---

## Navigation Structure

```
Asset Management Module
│
├── Dashboard (/assets/dashboard)
│   ├── Stats Overview
│   ├── Assets by Category
│   ├── Recent Maintenance
│   └── Quick Actions
│
├── Assets List (/assets)
│   ├── Search & Filter
│   ├── Asset Cards
│   └── Add New Asset
│
├── Asset Details (/assets/{id})
│   ├── Asset Information
│   ├── Maintenance Schedule
│   └── Related Actions
│
├── Maintenance Tasks (/assets/maintenance)
│   ├── Task List
│   ├── Create Task
│   └── Task Details
│
└── Expenses (/assets/expenses)
    ├── Expense List
    ├── Total Expenses
    └── Approval Status
```

---

## User Roles & Access

| Role | Can View | Can Create | Can Edit | Can Delete | Can Approve |
|------|----------|------------|----------|------------|-------------|
| **Property Owner** | Own assets | Assets | Own assets | Own assets | Expenses |
| **Estate Manager** | All assets | Assets, Tasks, Expenses | All assets | - | - |
| **Technician** | Assigned assets | - | Task status | - | - |
| **Admin** | All | All | All | All | All |

---

## Quick Links After Login

Once logged in, you can quickly access:
- **Dashboard:** `/dashboard` (overview of all your activities)
- **Assets:** `/assets/dashboard` (asset management hub)
- **Messages:** `/messages` (communications)
- **Profile:** `/profile` (account settings)

---

## Notes for Public Users

If you're not logged in and try to access Asset Management:
1. You'll see a "Sign In" button in the navbar
2. The footer will show the link, but you'll be redirected to login
3. After login, you'll automatically be taken to the Asset Dashboard

---

## Contact & Support

If you have issues accessing Asset Management:
1. Visit the **Help Center** (in footer)
2. Use the **Contact** page
3. Check your account permissions with an administrator

---

Last Updated: 2025-10-18
