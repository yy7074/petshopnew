import 'package:get/get.dart';
import '../pages/splash/splash_page.dart';
import '../pages/auth/login_page.dart';
import '../pages/main/main_page.dart';
import '../pages/home/home_page.dart';
import '../pages/category/category_page.dart';
import '../pages/category/category_list_page.dart';
import '../pages/message/message_page.dart';
import '../pages/profile/profile_page.dart';
import '../pages/product/product_detail_page.dart';
import '../pages/search/search_page.dart';
import '../pages/test_payment_page.dart';
import '../pages/payment/payment_page.dart';
import '../pages/auction/auction_winner_order_page.dart';
import '../pages/auction/auction_test_page.dart';
import '../pages/wallet/wallet_page.dart';
import '../pages/store/store_page.dart';
import '../pages/bids/bid_records_page.dart';
import '../pages/seller/seller_products_page.dart';
import '../pages/publish/publish_product_page.dart';
import '../pages/ai_recognition/ai_pet_recognition_page.dart';
import '../pages/lottery/simple_lottery_wheel_page.dart';
import '../pages/lottery/simple_lottery_history_page.dart';
import '../pages/auction/limited_auction_page.dart';
import '../pages/brand/brand_zone_page.dart';
import '../pages/fixed_price/fixed_price_zone_page.dart';
import '../pages/transaction/transaction_query_page.dart';
import '../pages/local_delivery/local_delivery_page.dart';
import '../pages/recycling/recycling_query_page.dart';
import '../pages/partner/partner_agent_page.dart';
import '../pages/pet_breeding/pet_breeding_page.dart';
import '../pages/local_pickup/local_pickup_page.dart';
import '../pages/pet_valuation/pet_valuation_page.dart';
import '../pages/nearby_discovery/nearby_discovery_page.dart';
import '../pages/seller/seller_orders_page.dart';
import '../pages/seller/seller_shop_settings_page.dart';
import '../pages/seller/seller_analytics_page.dart';

class AppRoutes {
  static const String splash = '/splash';
  static const String login = '/login';
  static const String main = '/main';
  static const String home = '/home';
  static const String category = '/category';
  static const String categoryList = '/category-list';
  static const String message = '/message';
  static const String profile = '/profile';
  static const String productDetail = '/product-detail';
  static const String search = '/search';
  static const String testPayment = '/test-payment';
  static const String payment = '/payment';
  static const String auctionWinnerOrder = '/auction-winner-order';
  static const String auctionTest = '/auction-test';
  static const String wallet = '/wallet';
  static const String store = '/store';
  static const String bidRecords = '/bid-records';
  static const String sellerProducts = '/seller-products';
  static const String publishProduct = '/publish-product';
  static const String aiPetRecognition = '/ai-pet-recognition';
  static const String limitedAuction = '/limited-auction';
  static const String brandZone = '/brand-zone';
  static const String fixedPriceZone = '/fixed-price-zone';
  static const String transactionQuery = '/transaction-query';
  static const String localDelivery = '/local-delivery';
  static const String recyclingQuery = '/recycling-query';
  static const String partnerAgent = '/partner-agent';
  static const String petBreeding = '/pet-breeding';
  static const String localPickup = '/local-pickup';
  static const String petValuation = '/pet-valuation';
  static const String nearbyDiscovery = '/nearby-discovery';
  static const String sellerOrders = '/seller-orders';
  static const String sellerShopSettings = '/seller-shop-settings';
  static const String sellerAnalytics = '/seller-analytics';
  static const String lottery = '/lottery';
  static const String lotteryHistory = '/lottery/history';

  static List<GetPage> routes = [
    GetPage(
      name: splash,
      page: () => const SplashPage(),
    ),
    GetPage(
      name: login,
      page: () => const LoginPage(),
    ),
    GetPage(
      name: main,
      page: () => const MainPage(),
    ),
    GetPage(
      name: home,
      page: () => const HomePage(),
    ),
    GetPage(
      name: category,
      page: () => const CategoryPage(),
    ),
    GetPage(
      name: categoryList,
      page: () {
        final arguments = Get.arguments as Map<String, dynamic>? ?? {};
        return CategoryListPage(
          categoryName: arguments['categoryName'] ?? '分类',
          subCategoryName: arguments['subCategoryName'],
          categoryId: arguments['categoryId'],
        );
      },
    ),
    GetPage(
      name: message,
      page: () => const MessagePage(),
    ),
    GetPage(
      name: profile,
      page: () => const ProfilePage(),
    ),
    GetPage(
      name: productDetail,
      page: () => ProductDetailPage(
        productData: Get.arguments is Map<String, dynamic>
            ? Get.arguments as Map<String, dynamic>
            : null,
      ),
    ),
    GetPage(
      name: search,
      page: () => const SearchPage(),
    ),
    GetPage(
      name: testPayment,
      page: () => const TestPaymentPage(),
    ),
    GetPage(
      name: payment,
      page: () {
        final arguments = Get.arguments as Map<String, dynamic>? ?? {};
        return PaymentPage(
          orderId: arguments['bidId'] ?? arguments['orderId'] ?? 0,
          totalAmount: (arguments['amount'] ?? 0.0).toDouble(),
          orderNo: arguments['orderNo'] ?? 'AUCTION_${arguments['bidId'] ?? 0}',
        );
      },
    ),
    GetPage(
      name: auctionWinnerOrder,
      page: () => const AuctionWinnerOrderPage(),
    ),
    GetPage(
      name: auctionTest,
      page: () => const AuctionTestPage(),
    ),
    GetPage(
      name: wallet,
      page: () => const WalletPage(),
    ),
    GetPage(
      name: store,
      page: () => StorePage(
        storeId: Get.arguments?['store_id'],
        sellerId: Get.arguments?['seller_id'],
      ),
    ),
    GetPage(
      name: bidRecords,
      page: () => const BidRecordsPage(),
    ),
    GetPage(
      name: sellerProducts,
      page: () => const SellerProductsPage(),
    ),
    GetPage(
      name: publishProduct,
      page: () => const PublishProductPage(),
    ),
    GetPage(
      name: aiPetRecognition,
      page: () => const AiPetRecognitionPage(),
    ),
    GetPage(
      name: limitedAuction,
      page: () => const LimitedAuctionPage(),
    ),
    GetPage(
      name: brandZone,
      page: () => const BrandZonePage(),
    ),
    GetPage(
      name: fixedPriceZone,
      page: () => const FixedPriceZonePage(),
    ),
    GetPage(
      name: transactionQuery,
      page: () => const TransactionQueryPage(),
    ),
    GetPage(
      name: localDelivery,
      page: () => const LocalDeliveryPage(),
    ),
    GetPage(
      name: recyclingQuery,
      page: () => const RecyclingQueryPage(),
    ),
    GetPage(
      name: partnerAgent,
      page: () => const PartnerAgentPage(),
    ),
    GetPage(
      name: petBreeding,
      page: () => const PetBreedingPage(),
    ),
    GetPage(
      name: localPickup,
      page: () => const LocalPickupPage(),
    ),
    GetPage(
      name: petValuation,
      page: () => const PetValuationPage(),
    ),
    GetPage(
      name: nearbyDiscovery,
      page: () => const NearbyDiscoveryPage(),
    ),
    GetPage(
      name: sellerOrders,
      page: () => const SellerOrdersPage(),
    ),
    GetPage(
      name: sellerShopSettings,
      page: () => const SellerShopSettingsPage(),
    ),
    GetPage(
      name: sellerAnalytics,
      page: () => const SellerAnalyticsPage(),
    ),
    GetPage(
      name: lottery,
      page: () => const SimpleLotteryWheelPage(),
    ),
    GetPage(
      name: lotteryHistory,
      page: () => const SimpleLotteryHistoryPage(),
    ),
  ];
}
